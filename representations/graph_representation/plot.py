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
    models = df_final['model_name'].unique()
    representations = df_final['representation'].unique()
    representation_colors = sns.color_palette("pastel")
    color_dict = {i: color for i, color in enumerate(representation_colors)}

    models = ["Mistral7BInstructv0.3.log", "MetaLlama3.18BInstructTurbo.log", "gemma29bit.log", 
            "gemma227bit.log", "Mixtral8x7BInstructv0.1.log", "MetaLlama370BInstructLite.log"]
    representations = df_final['representation'].unique()
    graph_files = sorted(df_final['graph_file'].unique(), key=extract_xy, reverse=False)

    # Set up the plot
    fig, axs = plt.subplots(2, 3, figsize=(20, 12))
    axs_list = [axs[0][0], axs[0][1], axs[0][2], axs[1][0], axs[1][1], axs[1][2]]
    bar_width = 0.15  # Increased bar width for better visibility

    # Calculate x positions once
    x = np.arange(len(models))

    for i, graph_file in enumerate(graph_files):
        ax = axs_list[i]
        
        for j, rep in enumerate(representations):
            accuracies_list = []
            for model in models:
                accuracy = df_final[
                    (df_final['representation'] == rep) & 
                    (df_final['graph_file'] == graph_file) & 
                    (df_final['query_hop_num'] == query_hop_num) & 
                    (df_final['shot_num'] == shot_num) & 
                    (df_final['model_name'] == model)
                ]['accuracy']
                accuracies_list.append(accuracy.iloc[0] if not accuracy.empty else 0)
            
            # Plot bars for this representation
            ax.bar(x + j*bar_width, 
                accuracies_list,
                bar_width,
                label=rep,
                color=color_dict[j])
        
        # Customize each subplot
        ax.set_xlabel(f'gnp_random_graph({graph_file})')
        ax.set_ylabel('Accuracy')
        ax.set_ylim(0, 1.1)
        ax.set_title(f'Graph: {graph_file}')
        
        # Set x-ticks in the middle of each group
        ax.set_xticks(x + bar_width * (len(representations)-1)/2)
        ax.set_xticklabels(models, rotation=45, ha='right')

    # Add single legend for entire figure
    handles, labels = axs_list[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.98), 
            ncol=min(4, len(representations)))

    # Adjust layout
    plt.tight_layout()
    plt.show()


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

