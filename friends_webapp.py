import streamlit as st
import pandas as pd
import ast
import plotly.graph_objects as go
from collections import Counter

# Set page layout to 'wide' to maximize screen space
st.set_page_config(layout="wide")

# Custom CSS for styling and layout improvements
st.markdown("""
    <style>
        /* General styling */
        .main-title { text-align: center; font-size: 42px; font-weight: bold; margin-top: 0; color: #f0f0f0; }
        .sub-title { text-align: center; font-size: 18px; color: #e0e0e0; margin-bottom: 5px; }
        .summary-text { font-size: 16px; color: #f0f0f0; text-align: justify; margin: 5px 0; padding: 0; }
        .nav-bar { display: flex; justify-content: flex-start; gap: 10px; margin-top: 0; }
        .stButton>button { margin-top: 0; }  /* Top-align buttons */
    </style>
""", unsafe_allow_html=True)

# Icons for navigation buttons
home_icon = "🏠 Home"
back_icon = "🔙 Back to Season"
stats_icon = "📊 Season Stats"

# Utility function to set navigation state
def set_navigation(page, season=None, episode=None):
    st.session_state["page"] = page
    st.session_state["current_season"] = season
    st.session_state["current_episode"] = episode

# Function to process the input DataFrame and structure data by season and episode
def process_data(df):
    episodes_data = {}
    
    # Iterate over each row and organize data by season and episode
    for _, row in df.iterrows():
        season = f"Season {row['season']}"
        episode_key = f"Episode {row['episode_number']}"
        
        # Initialize season and episode if not already in the dictionary
        if season not in episodes_data:
            episodes_data[season] = {}
        
        # Create episode dictionary with the required fields
        episodes_data[season][episode_key] = {
            "title": row["episode_title"],
            "summary": row["summary"],  # Placeholder summary
            "emotions": {
                row["emotion1"]: row["emotion1_prob"],
                row["emotion2"]: row["emotion2_prob"]
            },
            "topics": dict(zip(list(row["label"]), list(row["confidence"])))  # Zip label and confidence lists into a dictionary
        }
    
    return episodes_data

def plot_radar_chart_author_emotion(author_name, season, episode_number):
    data = pd.read_csv('emotions_hopefully_final.csv')
    data['author'] = data['author'].str.capitalize()
    # Filter data for the specified author, season, and episode
    author_data = data[(data['author'] == author_name) & 
                    (data['season'] == season) & 
                    (data['episode_number'] == episode_number)]
    # Count the top emotions in the selected episode
    emotion_counts = Counter(author_data['final_emotion_new'])
    # Extract labels and values for the radar chart
    labels = list(emotion_counts.keys())
    values = list(emotion_counts.values())
    
    # Create radar chart
    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name=f'Season {season}, Episode {episode_number}',
            marker_color='orange'  # Consistent color with other charts
        )
    )
    
    # Update layout for consistency with transparent background
    fig.update_layout(
        title=" ",  # Set title to an empty string to hide it
        title_x=0.5,
        title_y=0.99,
        polar=dict(
            bgcolor="rgba(0, 0, 0, 0)",  # Transparent polar background
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.1],  # Small margin above max value
                showline=True,
                linecolor='#f0f0f0',  # Light line color for readability
                gridcolor='gray',      # Light gray grid lines for contrast
                tickfont=dict(color='#f0f0f0')  # Light color for tick labels
            ),
            angularaxis=dict(
                showline=True,
                linecolor='#f0f0f0',   # Light color for angular axis lines
                tickfont=dict(color='#f0f0f0')  # Light color for tick labels
            )
        ),
        font=dict(color='#f0f0f0', size=10),  # Light font color for title and legend
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent main plot background
        paper_bgcolor="rgba(0, 0, 0, 0)"  # Transparent overall background
    )
    
    return fig

def character_wise_dialogue_count(main_characters, season):
    data = pd.read_csv('emotions_hopefully_final.csv')
    data['author'] = data['author'].str.capitalize()
    ## Count dialogues of each character aggregated over season and display using bar graph
    character_dialogues = data['author'].value_counts().to_dict()
    character_dialogues = {k: v for k, v in character_dialogues.items() if k in main_characters}
    character_dialogues = dict(sorted(character_dialogues.items(), key=lambda x: x[1], reverse=True))
    return character_dialogues

def emotions_pie_chart(season):
    ## Aggregate the emotions by season and display using pie chart
    data = pd.read_csv('emotions_hopefully_final.csv')
    data['author'] = data['author'].str.capitalize()
    season_data = data[data['season'] == season]
    emotion_counts = season_data['final_emotion_new'].value_counts().to_dict()
    print(emotion_counts)
    return emotion_counts

def plot_radar_chart_author_emotion_per_season(author_name, season):
    # Load the data
    data = pd.read_csv('emotions_hopefully_final.csv')
    data['author'] = data['author'].str.capitalize()
    
    # Filter data for the specified author and season
    author_data = data[(data['author'] == author_name) & (data['season'] == season)]
    # Count the occurrences of each emotion in the selected season
    emotion_counts = Counter(author_data['final_emotion_new'])
    
    # Extract labels (emotions) and values (counts) for the radar chart
    labels = list(emotion_counts.keys())
    values = list(emotion_counts.values())
    
    # Check if values is empty, return a placeholder chart if no data is available
    if not values:
        fig = go.Figure()
        fig.add_annotation(
            text="No emotion data available for this character in this season.",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            title=" ",  # Invisible title to prevent KeyError
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    # Create radar chart
    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name=f'Season {season}',
            marker_color='orange'  # Set marker color to orange
        )
    )
    
    # Update layout for transparent background
    fig.update_layout(
        title=" ",  # Set title to an empty string to hide it
        polar=dict(
            bgcolor="rgba(0,0,0,0)",  # Transparent polar background
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.1],  # Small margin above max value for visibility
                showline=True,
                linecolor='#f0f0f0',  # Light line color for readability
                gridcolor='gray',      # Light gray grid lines for contrast
                tickfont=dict(color='#f0f0f0')  # Light color for tick labels
            ),
            angularaxis=dict(
                showline=True,
                linecolor='#f0f0f0',   # Light color for angular axis lines
                tickfont=dict(color='#f0f0f0')  # Light color for tick labels
            )
        ),
        font=dict(color='#f0f0f0', size=10),  # Light font color for axis labels and legend
        showlegend=True,
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent main plot background
        paper_bgcolor="rgba(0, 0, 0, 0)"  # Transparent overall background
    )
    
    return fig

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "current_season" not in st.session_state:
    st.session_state["current_season"] = None
if "current_episode" not in st.session_state:
    st.session_state["current_episode"] = None

# Placeholder function to display the Home Page with Season Selection in a Horizontal Layout
def display_home(episodes_data):
    st.markdown("<h1 class='main-title'>Friends Library</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-title'>Explore all seasons and episodes</h2>", unsafe_allow_html=True)
    
    cols = st.columns(5)  # Arrange seasons in rows of 5
    for i, season in enumerate(episodes_data.keys()):
        with cols[i % 5]:  # Arrange buttons in a row of 5 per line
            if st.button(season, on_click=set_navigation, args=("season", season), key=season, help="View episodes"):
                pass


# Placeholder function to display Season Page with Episode Titles in a Horizontal Layout
def display_season(episodes_data, season):
    # Navigation bar at the top
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    if st.button(home_icon, on_click=set_navigation, args=("home",)):
        pass
    if st.button(stats_icon, on_click=set_navigation, args=("season_stats", season), key="stats"):
        pass
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.title(season)
    st.markdown("<h3 class='sub-title'>Select an Episode</h3>", unsafe_allow_html=True)
    
    # CSS to set a fixed width and height for episode buttons
    st.markdown("""
        <style>
        .fixed-button {
            width: 200px;  /* Set fixed width */
            height: 60px;  /* Set fixed height */
            text-align: center;
            white-space: nowrap;  /* Prevent text wrapping */
            overflow: hidden;     /* Hide overflow text if it exceeds button width */
        }
        .stButton>button {
            width: 100%;  /* Ensure buttons take full width within container */
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(5)  # Arrange episodes in rows of 5
    for i, episode_key in enumerate(episodes_data[season].keys()):
        episode_title = episodes_data[season][episode_key]["title"]
        episode_number = int(float(episode_key.split(" ")[1]))  # Convert episode key to integer
        display_text = f"Episode {episode_number}: {episode_title}"  # Combine episode number and title
        
        with cols[i % 5]:
            # Apply CSS class to the button for consistent sizing
            if st.button(display_text, on_click=set_navigation, args=("episode", season, episode_key), key=episode_key):
                pass

# Placeholder function to display Episode Details with Season Statistics Button
def display_episode(episodes_data, season, episode_key):
    # Navigation bar at the top
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    if st.button(home_icon, on_click=set_navigation, args=("home",)):
        pass
    if st.button(back_icon, on_click=set_navigation, args=("season", season)):
        pass
    st.markdown("</div>", unsafe_allow_html=True)
    
    details = episodes_data[season][episode_key]

    # Extract episode number as an integer
    episode_number = int(float(episode_key.split(" ")[1]))
    season_number = int(float(season.split(" ")[1]))
    # Display episode title with episode number
    st.title(f"Episode {episode_number}: {details['title']}")
    st.markdown(f"<p class='summary-text'>{details['summary']}</p>", unsafe_allow_html=True)

    # Display Emotions and Topics Charts below the text in a single horizontal row
    col1, col2 = st.columns(2)

    # Interactive Bar Chart for Emotions
    with col1:
        st.subheader("Top Emotions")
        emotions_df = pd.DataFrame(list(details["emotions"].items()), columns=["Emotion", "Value"])
        fig_emotions = go.Figure(go.Bar(
            x=emotions_df["Emotion"],
            y=emotions_df["Value"],
            marker_color='skyblue',
            text=emotions_df["Value"],
            textposition='auto'
        ))
        fig_emotions.update_layout(
            title_text="Top Emotions",
            title_x=0.5,
            font=dict(color='#f0f0f0', size=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        fig_emotions.update_xaxes(showline=True, linewidth=0.5, linecolor='#f0f0f0', color='#f0f0f0')
        fig_emotions.update_yaxes(showline=True, linewidth=0.5, linecolor='#f0f0f0', color='#f0f0f0')
        st.plotly_chart(fig_emotions, use_container_width=True)

    # Pie Chart for Topics with Confidence Scores
    with col2:
        st.subheader("Topic Confidence")
        topics_df = pd.DataFrame(list(details["topics"].items()), columns=["Topic", "Confidence"])
        fig_topics = go.Figure(go.Pie(
            labels=topics_df["Topic"].tolist(),     # Ensure this is a list of full topic names
            values=topics_df["Confidence"].tolist(),  # Ensure this is a list of confidence values
            textinfo='label+percent',
            insidetextorientation='radial',
            marker=dict(line=dict(color='#f0f0f0', width=1))
        ))
        fig_topics.update_layout(
            title_text="Topic Confidence Scores",
            title_x=0.5,
            font=dict(color='#f0f0f0', size=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_topics, use_container_width=True)
    
    # 3x2 Grid for Character-wise Radar Charts
    st.subheader("Character Emotion Radar Charts")
    character_names = ["Rachel", "Monica", "Phoebe", "Joey", "Chandler", "Ross"]  # List of main characters

    # Display characters in a 3x2 grid
    char_cols = st.columns(3)  # Set up three columns
    for i, character in enumerate(character_names):
        with char_cols[i % 3]:  # Use modulo to wrap characters in rows of 3
            st.markdown(f"#### {character}")
            radar_chart = plot_radar_chart_author_emotion(character, season_number, episode_number)
            st.plotly_chart(radar_chart, use_container_width=True)

        # After every third character, create a new row
        if (i + 1) % 3 == 0 and i + 1 < len(character_names):
            char_cols = st.columns(3)  # Create new row with three columns

def display_season_stats(season):
    character_names = ["Rachel", "Monica", "Phoebe", "Joey", "Chandler", "Ross"]  # Main characters
    # Back button to return to the season page
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    if st.button(back_icon, on_click=set_navigation, args=("season", season)):
        pass
    st.markdown("</div>", unsafe_allow_html=True)
    season_number = int(float(season.split(" ")[1]))
    st.title(f"Season Statistics: {season}")
    
    # 1. Character-Wise Dialogue Count Bar Chart
    st.subheader("Character-Wise Dialogue Count")
    dialogue_data = character_wise_dialogue_count(character_names, season)  # Get data as a dictionary
    
    # Process the dictionary to create lists for plotting
    characters = list(dialogue_data.keys())
    dialogue_counts = list(dialogue_data.values())
    
    fig_dialogues = go.Figure(go.Bar(
        x=characters,  # Character names on x-axis
        y=dialogue_counts,  # Dialogue counts on y-axis
        text=dialogue_counts,
        textposition='auto',
        marker_color='blue'
    ))
    fig_dialogues.update_layout(
        title="Dialogue Count by Character",
        xaxis_title="Character",
        yaxis_title="Dialogue Count",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color='#f0f0f0')
    )
    st.plotly_chart(fig_dialogues, use_container_width=True)

    # 2. Emotions Pie Chart
    st.subheader("Emotions Distribution")
    emotions_data = emotions_pie_chart(season_number)  # Get data from your function
    emotions = list(emotions_data.keys())
    counts = list(emotions_data.values())
    fig_emotions = go.Figure(go.Pie(
        labels=emotions,  # Assuming emotions_data has columns Emotion and Count
        values=counts,
        textinfo='label+percent',
        insidetextorientation='radial',
        marker=dict(line=dict(color='#f0f0f0', width=1))
    ))
    fig_emotions.update_layout(
        title="Emotions in Season",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color='#f0f0f0')
    )
    st.plotly_chart(fig_emotions, use_container_width=True)

    # 3. Character-Specific Radar Charts for Emotions
    st.subheader("Character Emotion Profiles")
    character_names = ["Rachel", "Monica", "Phoebe", "Joey", "Chandler", "Ross"]  # Main characters
    
    # Arrange radar charts in a 3x2 grid
    char_cols = st.columns(3)  # Set up three columns for the 3x2 grid
    for i, character in enumerate(character_names):
        with char_cols[i % 3]:  # Use modulo to wrap characters in rows of 3
            st.markdown(f"#### {character}")
            radar_chart = plot_radar_chart_author_emotion_per_season(character, season_number)
            st.plotly_chart(radar_chart, use_container_width=True, key=f"radar_chart_{character}_{season_number}")

        # After every third character, create a new row
        if (i + 1) % 3 == 0 and i + 1 < len(character_names):
            char_cols = st.columns(3)  # Start a new row


df = pd.read_csv("frontend_data.csv")
df['label'] = df['label'].apply(ast.literal_eval)
df['confidence'] = df['confidence'].apply(ast.literal_eval)

# Process the DataFrame to get episode data
episodes_data = process_data(df)

# Page Navigation Logic
if st.session_state["page"] == "home":
    display_home(episodes_data)
elif st.session_state["page"] == "season" and st.session_state["current_season"]:
    display_season(episodes_data, st.session_state["current_season"])
elif st.session_state["page"] == "episode" and st.session_state["current_season"] and st.session_state["current_episode"]:
    display_episode(episodes_data, st.session_state["current_season"], st.session_state["current_episode"])
elif st.session_state["page"] == "season_stats" and st.session_state["current_season"]:
    display_season_stats(st.session_state["current_season"])  # Call to season stats page