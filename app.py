import os
import pandas as pd
import streamlit as st
import speech_recognition as sr
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize feedback directory and files
feedback_dir = 'feedback'
os.makedirs(feedback_dir, exist_ok=True)

positive_feedback_file = os.path.join(feedback_dir, 'positive_feedback.csv')
neutral_feedback_file = os.path.join(feedback_dir, 'neutral_feedback.csv')
negative_feedback_file = os.path.join(feedback_dir, 'negative_feedback.csv')
combined_feedback_file = os.path.join(feedback_dir, 'combined_feedback.csv')

# Load your sentiment analysis model and vectorizer
filename = 'saved_model.sav'
with open(filename, 'rb') as model_file:
    saved_model = pickle.load(model_file)

vectorizer_filename = 'tfidf_vectorizer.sav'
with open(vectorizer_filename, 'rb') as vectorizer_file:
    tfidf_vectorizer = pickle.load(vectorizer_file)

# Function to store feedback
def store_feedback(text, sentiment):
    global positive_feedback_file, neutral_feedback_file, negative_feedback_file, combined_feedback_file

    # Create files with headers if they do not exist
    if not os.path.exists(positive_feedback_file):
        pd.DataFrame(columns=['text', 'sentiment']).to_csv(positive_feedback_file, index=False)
    if not os.path.exists(neutral_feedback_file):
        pd.DataFrame(columns=['text', 'sentiment']).to_csv(neutral_feedback_file, index=False)
    if not os.path.exists(negative_feedback_file):
        pd.DataFrame(columns=['text', 'sentiment']).to_csv(negative_feedback_file, index=False)

    # Append feedback to the appropriate file
    if sentiment == 'positive':
        df = pd.DataFrame({'text': [text], 'sentiment': [1]})
        df.to_csv(positive_feedback_file, mode='a', header=False, index=False)
    elif sentiment == 'neutral':
        df = pd.DataFrame({'text': [text], 'sentiment': [2]})
        df.to_csv(neutral_feedback_file, mode='a', header=False, index=False)
    else:
        df = pd.DataFrame({'text': [text], 'sentiment': [0]})
        df.to_csv(negative_feedback_file, mode='a', header=False, index=False)

    # Update combined file
    combined_df = pd.concat([pd.read_csv(positive_feedback_file),
                             pd.read_csv(neutral_feedback_file),
                             pd.read_csv(negative_feedback_file)], ignore_index=True)
    combined_df.to_csv(combined_feedback_file, index=False)

# Function to load feedback
def load_feedback():
    try:
        pos_df = pd.read_csv(positive_feedback_file)
    except pd.errors.EmptyDataError:
        pos_df = pd.DataFrame(columns=['text', 'sentiment'])
    try:
        neu_df = pd.read_csv(neutral_feedback_file)
    except pd.errors.EmptyDataError:
        neu_df = pd.DataFrame(columns=['text', 'sentiment'])
    try:
        neg_df = pd.read_csv(negative_feedback_file)
    except pd.errors.EmptyDataError:
        neg_df = pd.DataFrame(columns=['text', 'sentiment'])

    combined_df = pd.concat([pos_df, neu_df, neg_df], ignore_index=True)
    return pos_df, neu_df, neg_df, combined_df

# Function to predict sentiment
def predict_sentiment(text):
    text_tfidf = tfidf_vectorizer.transform([text])
    prediction = saved_model.predict(text_tfidf)
    return prediction[0]

# Function to handle voice commands
def handle_voice_command(command):
    if 'show last' in command:
        try:
            num = int(command.split()[-1])
        except ValueError:
            num = 5  # Default to show last 5 if no specific number is mentioned
        pos_df, neu_df, neg_df, combined_df = load_feedback()
        st.subheader(f"Last {num} Feedback Entries")
        st.write(combined_df.tail(num))
    elif 'show +ve' in command or 'show positive' in command:
        pos_df, _, _, _ = load_feedback()
        st.subheader("Positive Feedback Entries")
        st.write(pos_df)
    elif 'show -ve' in command or 'show negative' in command:
        _, _, neg_df, _ = load_feedback()
        st.subheader("Negative Feedback Entries")
        st.write(neg_df)
    elif 'show neutral' in command:
        _, neu_df, _, _ = load_feedback()
        st.subheader("Neutral Feedback Entries")
        st.write(neu_df)
    elif 'count +ve' in command or 'count positive' in command:
        pos_df, _, _, _ = load_feedback()
        st.subheader("Count of Positive Feedback Entries")
        st.write(len(pos_df))
    elif 'count -ve' in command or 'count negative' in command:
        _, _, neg_df, _ = load_feedback()
        st.subheader("Count of Negative Feedback Entries")
        st.write(len(neg_df))
    elif 'count neutral' in command:
        _, neu_df, _, _ = load_feedback()
        st.subheader("Count of Neutral Feedback Entries")
        st.write(len(neu_df))
    else:
        st.warning("Command not recognized. Please try again.")

# Function to recognize voice input
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            st.write(f"Command recognized: {text}")
            return text.lower()
        except sr.UnknownValueError:
            st.warning("Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")

# # Function to plot line and density graphs based on prediction results
# def plot_prediction_graphs():
#     pos_df, neu_df, neg_df, combined_df = load_feedback()
#     if len(combined_df) > 0:
#         # Plot line graph of sentiment counts
#         plt.figure(figsize=(10, 6))
#         sns.countplot(x='sentiment', data=combined_df)
#         plt.title('Sentiment Distribution')
#         plt.xlabel('Sentiment')
#         plt.ylabel('Count')
#         st.pyplot()

#         # Plot density graph of sentiment scores
#         plt.figure(figsize=(10, 6))
#         sns.kdeplot(data=combined_df['sentiment'], shade=True)
#         plt.title('Sentiment Density')
#         plt.xlabel('Sentiment')
#         plt.ylabel('Density')
#         st.pyplot()
#     else:
#         st.warning("No feedback entries to plot.")

# Main function to run the app
def main():
    st.title("Feedback Analysis App with Voice Access")

    # User input for feedback
    feedback_text = st.text_input("Enter your feedback here:")

    # Sentiment prediction and storage
    if st.button("Submit Feedback"):
        sentiment_label = predict_sentiment(feedback_text)
        store_feedback(feedback_text, sentiment_label)
        st.success(f"{sentiment_label.capitalize()} feedback submitted.")

    # Voice command handling
    if st.button("Voice Command"):
        command = recognize_speech()
        if command:
            handle_voice_command(command)

    # Display feedback analysis
    st.header("Feedback Analysis")
    pos_df, neu_df, neg_df, combined_df = load_feedback()
    st.subheader("Combined Feedback Entries")
    st.write(combined_df)

    # Debugging - Print input and prediction
    st.write(f"Input Text: {feedback_text}")
    st.write(f"Predicted Sentiment: {predict_sentiment(feedback_text)}")

    # # Analyze button for plotting graphs
    # if st.button("Analyze"):
    #     plot_prediction_graphs()

if __name__ == "__main__":
    main()
