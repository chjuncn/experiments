import numpy as np
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
import plotly.express as px



onehope_20compolexity = "/Users/chjun/Downloads/10102024 - graph retrieval experiments - 1.2plot.csv"
onehope_50compolexity = "/Users/chjun/Downloads/10102024 - graph retrieval experiments - 2.2plot.csv"
twohope_20compolexity = "/Users/chjun/Downloads/10102024 - graph retrieval experiments - 3.2plot.csv"

# representation_names = ['baseline', 'node_id[-4:]+edge_id', 'node_id+edge_id', "randomStr+edge_id", "<edge_id>", "node_id[:4]+edge_id", "<key=>node_id AND node_id[:4]+edge_id"]  # Replace with your actual list

def process_csv(csv_path, query_hop_num="1", graph_complexity="0.2"):
    df = pd.read_csv(csv_path, header=0)

        # Print the actual number of columns
    num_columns = len(df.columns)
    num_rows = len(df)
    print(f"Number of columns in the CSV: {len(df.columns)}")
    print(f"Number of rows in the CSV: {len(df)}")
    if num_rows != 43:
        df = df.iloc[:42, :]
    # Print the first few rows of the DataFrame to see its structure
    print(df.head())
    if num_columns > 8:
        df = df.iloc[:, :8]
    elif num_columns < 8:
        raise ValueError("CSV must have at least 8 columns")
    print(df.head())

    df.columns = ['model', 'unused', '5', '10', '15', '20', "25", "30"]
    # Drop the unused column
    df = df.drop('unused', axis=1)

    for col in ['5', '10', '15', '20', "25", "30"]:
        df[col] = pd.to_numeric(df[col].replace('#REF!', np.nan), errors='coerce') 
        df[col] = pd.to_numeric(df[col].replace('#DIV/0!', np.nan), errors='coerce')

    # Melt the dataframe to get the desired structure
    df_melted = df.melt(id_vars=['model'], var_name='size', value_name='accuracy')

    # Convert size to integer
    df_melted['size'] = pd.to_numeric(df_melted['size'], errors='coerce')
    # # Remove rows with NaN values
    # df_final = df_final.dropna()

    # Add a representation column
    df_melted['representation'] = df_melted.groupby(['model', 'size']).cumcount() + 1
    name_mapping = {i+1: name for i, name in enumerate(representation_names)}
    df_melted['representation'] = df_melted['representation'].map(name_mapping)

    # Reorder columns
    df_final = df_melted[['model', 'representation', 'size', 'accuracy']]
    df_final['graph_complexity'] = graph_complexity
    df_final['query_hop_num'] = query_hop_num
    # Reset index
    df_final = df_final.reset_index(drop=True)

    # Display the first few rows of the resulting dataframe
    print(df_final.head(28))

    # Optionally, save to a CSV file
    # df_final.to_csv('transformed_data.csv', index=False)

    # Verify that we have 7 representations for each model and size
    verification = df_final.groupby(['model', 'size']).size().unique()
    print("\nNumber of representations for each model and size combination:", verification)

    return df_final

def shorten_model_name(model_name):
    index = model_name.find('/')
    return model_name[index+1: index+18]


def showgraph_claude(df_final, query_hop_num=1, shot_num=0):
    print(df_final)
    models = df_final['model_name'].unique()
    for i, model in enumerate(models):
        if isinstance(model, str):
            models[i] = shorten_model_name(model)
    representations = df_final['representation'].unique()
    representation_colors = sns.color_palette("pastel", n_colors=7)
    color_dict = {}
    for i, color in enumerate(representation_colors):
        color_dict[i] = color

    # models = df['model_name'].unique()
    models = ["Mistral7BInstructv0.3.log", "MetaLlama3.18BInstructTurbo.log", "gemma29bit.log", "gemma227bit.log", "Mixtral8x7BInstructv0.1.log", "MetaLlama370BInstructLite.log"]
    representations = df_final['representation'].unique()
    graph_files = sorted(df_final['graph_file'].unique(), key=extract_xy, reverse=False)

    # Set up the plot
    fig, axs = plt.subplots(2, 3, figsize=(10, 10))
    axs_list = [axs[0][0], axs[0][1], axs[0][2], axs[1][0], axs[1][1], axs[1][2]]
    # Set width of bar
    bar_width = 0.1

    # Set position of bar on X axis
    r = np.arange(len(models))
    # Make the plot
    for i , graph_file in enumerate(graph_files):
        ax = axs_list[i]
        for j, rep in enumerate(representations):
            color = color_dict[j]
            accuracies = df_final[((df_final['representation'] == rep) & (df_final['graph_file'] == graph_file) 
                                   & (df_final['query_hop_num'] == query_hop_num) 
                                   & (df_final['shot_num'] == shot_num))]['accuracy']
            position = [x + bar_width*j for x in r]
            print(accuracies)
            pad_length = 6 - len(accuracies)
            if pad_length > 0:
                accuracies = np.concatenate([accuracies, np.zeros(pad_length)])
            # ax.bar(position, accuracies, width=bar_width, label=rep, color=color)
            ax.bar(position, accuracies, width=bar_width, label=rep, color=color)

            
        
        # Add xticks on the middle of the group bars
        ax.set_xlabel(f'gnp_random_graph({graph_file})')
        ax.set_ylabel('Accuracy')
        ax.set_ylim(0, 1.1)
        ax.set_title('Model Accuracy by Representation')
        ax.set_xticks([r + bar_width for r in range(len(models))], models, rotation=45, ha='right')
        handles, labels = ax.get_legend_handles_labels()
        
    fig.legend(handles, labels, loc='upper center', ncols=7)

    # Create legend & Show graphic
    # plt.legend(title='Representation', bbox_to_anchor=(1.05, 1), loc='best', ncols=7)
    plt.tight_layout()
    # plt.legend(title='Representation', loc='upper left', ncols=7)

    plt.show()


def plot_combined_data_claude(df_final_1, df_final_2, df_final_3):
    # Combine the two dataframes
    df_combined = pd.concat([df_final_1, df_final_2, df_final_3])
    
    # Create a color palette for representations
    representation_colors = sns.color_palette("husl", n_colors=7)
    color_dict = {}
    for i, color in enumerate(representation_colors):
        color_dict[representation_names[i]] = color

    # Create the plot
    fig, axs = plt.subplots(2, 3, figsize=(10, 10))
    axs_list = [axs[0][0], axs[0][1], axs[0][2], axs[1][0], axs[1][1], axs[1][2]]
    
    # Plot for graph complexity 20
    size = 5
    for i, model in enumerate(df_final_1['model'].unique()):
        ax = axs_list[i]
        for rep in df_final_1['representation'].unique():
            data = df_final_1[(df_final_1['model'] == model) & (df_final_1['representation'] == rep) & (df_final_1['size'] == size)]
            ax.plot(data['representation'], data['accuracy'], marker='o', linestyle='none', label=rep, color=color_dict[rep])
    
    # Plot for graph complexity 30
            data = df_final_2[(df_final_2['model'] == model) & (df_final_2['representation'] == rep) & (df_final_2['size'] == size)]
            ax.plot(data['representation'], data['accuracy'], marker='>', linestyle='none', label=rep, color=color_dict[rep])
            data = df_final_3[(df_final_3['model'] == model) & (df_final_3['representation'] == rep) & (df_final_3['size'] == size)]
            ax.plot(data['representation'], data['accuracy'], marker='<', linestyle='none', label=rep, color=color_dict[rep])
        
        ax.set_title(f'{model}')
        ax.set_xlabel('Representations')
        ax.set_ylabel('Accuracy')
        ax.set_xticks([r  for r in range(len(representation_names))], representation_names, rotation=45, ha='right')
        ax.set_ylim(0, 1.1)  # Set y-axis limit from 0 to 1.1 for better visibility    

    plt.tight_layout()
    plt.savefig('combined_accuracy_plot.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_combined_data_3d(df_final_1, df_final_2, df_final_3):
    # Create a color palette for representations
    representation_colors = sns.color_palette("husl", n_colors=7)
    color_dict = {}
    for i, color in enumerate(representation_colors):
        color_dict[representation_names[i]] = color

    # Create the plot
    fig, axs = plt.subplots(2, 3, figsize=(10, 10))
    axs_list = [axs[0][0], axs[0][1], axs[0][2], axs[1][0], axs[1][1], axs[1][2]]
    
    # Plot for graph complexity 20
    size = 5
    for i, model in enumerate(df_final_1['model'].unique()):
        ax = axs_list[i]
        X, Y, Z = [], [], []
        for rep in df_final_1['representation'].unique():
            data = df_final_1[(df_final_1['model'] == model) & (df_final_1['representation'] == rep) & (df_final_1['size'] == size)]
            Z.append(data['accuracy'])
    # Plot for graph complexity 30
            data = df_final_2[(df_final_2['model'] == model) & (df_final_2['representation'] == rep) & (df_final_2['size'] == size)]
            ax.plot(data['representation'], data['accuracy'], marker='>', linestyle='none', label=rep, color=color_dict[rep])
            X.append(data['accuracy'])  
            data = df_final_3[(df_final_3['model'] == model) & (df_final_3['representation'] == rep) & (df_final_3['size'] == size)]
            Y.append(data['accuracy'])
        
        ax.set_title(f'{model}')
        ax.set_xlabel('Representations')
        ax.set_ylabel('Accuracy')
        # ax.set_xticks([r  for r in range(len(representation_names))], representation_names, rotation=45, ha='right')
        ax.set_ylim(0, 1.1)  # Set y-axis limit from 0 to 1.1 for better visibility    
        ax.scatter(X, Y, Z)

    plt.tight_layout()
    plt.savefig('combined_accuracy_plot.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_combined_data_3d_claude(df_final_1, df_final_2, df_final_3):
    # Create a color palette for representations
    representation_names = df_final_1['representation'].unique()
    representation_colors = sns.color_palette("husl", n_colors=len(representation_names))
    color_dict = dict(zip(representation_names, representation_colors))

    # Create the plot
    fig = plt.figure(figsize=(20, 15))
    
    for i, model in enumerate(df_final_1['model'].unique()):
        ax = fig.add_subplot(2, 3, i+1, projection='3d')
        
        X, Y, Z = [], [], []
        C = []  # For colors
        
        for rep in representation_names:
            data1 = df_final_1[(df_final_1['model'] == model) & (df_final_1['representation'] == rep)]
            data2 = df_final_2[(df_final_2['model'] == model) & (df_final_2['representation'] == rep)]
            data3 = df_final_3[(df_final_3['model'] == model) & (df_final_3['representation'] == rep)]
            
            if not (data1.empty or data2.empty or data3.empty):
                X.append(data1['accuracy'].values[0])
                Y.append(data2['accuracy'].values[0])
                Z.append(data3['accuracy'].values[0])
                C.append(color_dict[rep])
        
        scatter = ax.scatter(X, Y, Z, c=C, s=100)
        
        ax.set_title(f'{model}')
        ax.set_xlabel('Dataset 1 Accuracy')
        ax.set_ylabel('Dataset 2 Accuracy')
        ax.set_zlabel('Dataset 3 Accuracy')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_zlim(0, 1)

    # Add a color bar
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.hsv), ax=fig.axes)
    cbar.set_ticks(np.linspace(0, 1, len(representation_names)))
    cbar.set_ticklabels(representation_names)
    
    plt.tight_layout()
    plt.savefig('combined_3d_accuracy_plot.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_impact_heatmap(df_final_1, df_final_2, df_final_3):
    models = df_final_1['model'].unique()
    representations = df_final_1['representation'].unique()
    sizes = df_final_1['size'].unique()

    fig = make_subplots(rows=2, cols=3, 
                        subplot_titles=models,
                        x_title="Sizes",
                        y_title="Representations",
                        shared_xaxes=True,
                        shared_yaxes=True)

    for i, model in enumerate(models):
        row = i // 3 + 1
        col = i % 3 + 1

        # Create impact matrices
        impact_complexity = pd.DataFrame(index=representations, columns=sizes)
        impact_hop = pd.DataFrame(index=representations, columns=sizes)

        for rep in representations:
            for size in sizes:
                # if size != 5:
                #     break
                base_acc = df_final_1[(df_final_1['model'] == model) & 
                                      (df_final_1['representation'] == rep) & 
                                      (df_final_1['size'] == size)]['accuracy'].values[0]
                
                complex_acc = df_final_2[(df_final_2['model'] == model) & 
                                         (df_final_2['representation'] == rep) & 
                                         (df_final_2['size'] == size)]['accuracy'].values[0]
                
                hop_acc = df_final_3[(df_final_3['model'] == model) & 
                                     (df_final_3['representation'] == rep) & 
                                     (df_final_3['size'] == size)]['accuracy'].values[0]
                
                impact_complexity.loc[rep, size] = complex_acc - base_acc
                impact_hop.loc[rep, size] = hop_acc - base_acc

        # Create heatmaps
        heatmap_complexity = go.Heatmap(
            z=impact_complexity.values,
            x=sizes,
            y=representations,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            name='Graph Complexity Impact'
        )

        heatmap_hop = go.Heatmap(
            z=impact_hop.values,
            x=sizes,
            y=representations,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            name='Hop Number Impact'
        )

        fig.add_trace(heatmap_complexity, row=row, col=col)
        fig.add_trace(heatmap_hop, row=row, col=col)

    # Update layout
    fig.update_layout(
        title_text="Impact of Graph Complexity and Hop Number on Accuracy",
        height=1000,
        width=1500
    )

    # Show the plot
    fig.show()



def create_impact_comparison_heatmap(df_final_1, df_final_2, df_final_3):
    models = df_final_1['model'].unique()
    representations = df_final_1['representation'].unique()
    sizes = df_final_1['size'].unique()

    fig = make_subplots(rows=2, cols=3, 
                        subplot_titles=models,
                        x_title="Sizes",
                        y_title="Representations",
                        shared_xaxes=True,
                        shared_yaxes=True)

    for i, model in enumerate(models):
        row = i // 3 + 1
        col = i % 3 + 1

        # Create impact comparison matrix
        impact_comparison = pd.DataFrame(index=representations, columns=sizes)

        for rep in representations:
            for size in sizes:
                base_acc = df_final_1[(df_final_1['model'] == model) & 
                                      (df_final_1['representation'] == rep) & 
                                      (df_final_1['size'] == size)]['accuracy'].values[0]
                
                complex_acc = df_final_2[(df_final_2['model'] == model) & 
                                         (df_final_2['representation'] == rep) & 
                                         (df_final_2['size'] == size)]['accuracy'].values[0]
                
                hop_acc = df_final_3[(df_final_3['model'] == model) & 
                                     (df_final_3['representation'] == rep) & 
                                     (df_final_3['size'] == size)]['accuracy'].values[0]
                
                complexity_impact = abs(complex_acc - base_acc)
                hop_impact = abs(hop_acc - base_acc)
                
                # Positive values indicate complexity has more impact
                # Negative values indicate hop number has more impact
                impact_comparison.loc[rep, size] = complexity_impact - hop_impact

        # Create heatmap
        heatmap = go.Heatmap(
            z=impact_comparison.values,
            x=sizes,
            y=representations,
            colorscale=[
                [0, 'blue'],
                [0.5, 'white'],
                [1, 'red']
            ],
            zmin=-1,
            zmax=1,
            colorbar=dict(
                title="Impact Difference",
                tickvals=[-1, 0, 1],
                ticktext=["Hop Number", "Equal", "Complexity"]
            )
        )

        fig.add_trace(heatmap, row=row, col=col)

        # Add annotations for the most significant impacts
        for rep in representations:
            for size in sizes:
                value = impact_comparison.loc[rep, size]
                if abs(value) > 0.1:  # Adjust this threshold as needed
                    annotation_text = "C" if value > 0 else "H"
                    fig.add_annotation(
                        x=size, y=rep,
                        text=annotation_text,
                        showarrow=False,
                        font=dict(color="black", size=10),
                        row=row, col=col
                    )

    # Update layout
    fig.update_layout(
        title_text="Impact Comparison: Graph Complexity vs Hop Number",
        height=1000,
        width=1500
    )

    # Show the plot
    fig.show()



# Load the d
def extract_xy(filename):
    match = re.search(r'gnp_n(\d+)_p(\d+)', filename)
    if match:
        res = int(match.group(2)), int(match.group(1))
    else:
        res = (0, 0)
    return res

# Create a function to generate heatmaps
def generate_accuracy_heatmaps(df, hop_num, shot_num):
    df['accuracy'] = df['total_score'] / df['full_score']
    
    # Get unique values
    models = df['model_name'].unique()
    models = ["Mistral7BInstructv0.3.log", "MetaLlama3.18BInstructTurbo.log", "gemma29bit.log", "gemma227bit.log", "Mixtral8x7BInstructv0.1.log", "MetaLlama370BInstructLite.log"]
    representations = df['representation'].unique()
    graph_files = sorted(df['graph_file'].unique(), key=extract_xy, reverse=False)

    # Create subplots
    fig = make_subplots(rows=2, cols=3, 
                        subplot_titles=models,
                        x_title="Graph Files",
                        y_title="Representations",
                        shared_xaxes=True,
                        shared_yaxes=True)

    for i, model in enumerate(models):
        row = i // 3 + 1
        col = i % 3 + 1

        # Create impact comparison matrix
        accuracy_data = pd.DataFrame(index=representations, columns=graph_files)

        for rep in representations:
            for graph in graph_files:
                model_data = df[(df['model_name'] == model) & 
                                (df['representation'] == rep) & 
                                (df['graph_file'] == graph) &
                                (df['query_hop_num'] == hop_num) &
                                (df['shot_num'] == shot_num)]
                
                if not model_data.empty:
                    accuracy = model_data['accuracy'].values[0]
                    
                    # Positive values indicate higher fail rate relative to token utilization
                    # Negative values indicate lower fail rate relative to token utilization
                    accuracy_data.loc[rep, graph] = accuracy

        heatmap = go.Heatmap(
            z=accuracy_data.values,
            x=graph_files,
            y=representations,
            colorscale=px.colors.sequential.Viridis,  # You can change this to any colorscale you prefer
            zmin=0,
            zmax=1,
            colorbar=dict(
                title="Accuracy",
                tickvals=[0, 0.5, 1],
                ticktext=["0%", "50%", "100%"]
            )
        )

        fig.add_trace(heatmap, row=row, col=col)

    # Update layout
    fig.update_layout(
        title_text="Accuracy for Different Models",
        height=800,
        width=1200
    )

# Save the figure
    fig.show()  
    # fig.write_html("model_performance_heatmaps.html")
    print("Interactive heatmap has been generated and saved as 'model_performance_heatmaps.html'.")


def generate_error_reason_heatmaps(df, hop_num, shot_num):
    #late the ratio of wrong_edge_problem_num to failed_num
    df['wrong_edge_ratio'] = df['wrong_edge_problem'] / df['failed_num']
    df['wrong_edge_ratio'] = df['wrong_edge_ratio'].fillna(0)  # Handle division by zero

    # Get unique values and sort graph_files
    models = df['model_name'].unique()
    models = ["Mistral7BInstructv0.3.log", "MetaLlama3.18BInstructTurbo.log", "gemma29bit.log", "gemma227bit.log", "Mixtral8x7BInstructv0.1.log", "MetaLlama370BInstructLite.log"]
    representations = df['representation'].unique()
    graph_files = sorted(df['graph_file'].unique(), key=extract_xy, reverse=False)

    # Create subplots
    fig = make_subplots(rows=2, cols=3, 
                        subplot_titles=models,
                        x_title="Graph Files",
                        y_title="Representations",
                        shared_xaxes=True,
                        shared_yaxes=True)

    for i, model in enumerate(models):
        row = i // 3 + 1
        col = i % 3 + 1

        # Create wrong edge ratio matrix
        ratio_matrix = pd.DataFrame(index=representations, columns=graph_files)
        dominant_matrix = pd.DataFrame(index=representations, columns=graph_files)

        for rep in representations:
            for graph in graph_files:
                model_data = df[(df['model_name'] == model) & 
                                (df['representation'] == rep) & 
                                (df['graph_file'] == graph) &
                                (df['query_hop_num'] == hop_num) &
                                (df['shot_num'] == shot_num)]
                
                if not model_data.empty:
                    ratio = model_data['wrong_edge_ratio'].values[0]
                    ratio_matrix.loc[rep, graph] = ratio

        # Create heatmap
        heatmap = go.Heatmap(
            z=ratio_matrix.values,
            x=graph_files,
            y=representations,
            colorscale="purples",
            zmin=0,
            zmax=1,
            colorbar=dict(
                title="Wrong Edge Ratio",
                tickvals=[0, 0.5, 1],
                ticktext=["0%", "50%", "100%"]
            )
        )

        fig.add_trace(heatmap, row=row, col=col)


    # Update layout
    fig.update_layout(
        title_text="Wrong Edge Problem Analysis for Different Models",
        height=800,
        width=1200
    )

    # Save the figure
    fig.show()
    print("Interactive heatmap has been generated and saved as 'wrong_edge_problem_analysis.html'.")



def plot_token_utilization_heatmap():
    df =  load_json_to_df('test_summary.json')
    # generate_error_reason_heatmaps(df, 1, 0)
    # generate_error_reason_heatmaps(df, 2, 1)
    showgraph_claude(df, 1, 0)

    # Create a pivot table


def load_json_to_df(file):
    with open(file, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(df.head())
    return df




if __name__ == "__main__":
    # df_final_1 = process_csv(csv_path=onehope_20compolexity, query_hop_num="1", graph_complexity="0.2")
    # df_final_2 = process_csv(csv_path=onehope_50compolexity, query_hop_num="1", graph_complexity="0.5")
    # df_final_3 = process_csv(csv_path=twohope_20compolexity, query_hop_num="2", graph_complexity="0.2")
    # df_final_2 = process_csv(csv_path=onehope_50compolexity)
    # create_impact_comparison_heatmap(df_final_1, df_final_2, df_final_3)
    # showgraph_claude(df_final_3)
    plot_token_utilization_heatmap()


