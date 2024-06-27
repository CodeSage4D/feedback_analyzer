import os
import pandas as pd

# Create directories for feedback storage if not exists
feedback_dir = 'feedback'
os.makedirs(feedback_dir, exist_ok=True)

positive_feedback_file = os.path.join(feedback_dir, 'positive_feedback.csv')
neutral_feedback_file = os.path.join(feedback_dir, 'neutral_feedback.csv')
negative_feedback_file = os.path.join(feedback_dir, 'negative_feedback.csv')
combined_feedback_file = os.path.join(feedback_dir, 'combined_feedback.csv')

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

# Test the function with sample data
if __name__ == "__main__":
    # Sample data
    feedback_text = "I am so happy"
    sentiment_label = "positive"

    # Store the feedback
    store_feedback(feedback_text, sentiment_label)

    # Confirm stored data
    pos_df = pd.read_csv(positive_feedback_file)
    neu_df = pd.read_csv(neutral_feedback_file)
    neg_df = pd.read_csv(negative_feedback_file)
    combined_df = pd.read_csv(combined_feedback_file)

    print("Positive Feedback:")
    print(pos_df)
    print("\nNeutral Feedback:")
    print(neu_df)
    print("\nNegative Feedback:")
    print(neg_df)
    print("\nCombined Feedback:")
    print(combined_df)
