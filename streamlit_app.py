import streamlit as st
import pandas as pd
from collections import Counter

# ROC Action Keyword Mapping
roc_action_map = {
    "equipment": ["broken", "damaged", "jammed", "stuck", "faulty", "issue", "repair", "missing", "lost", "not working", "demo"],
    "cleanliness": ["dirty", "stinking", "smelly", "unhygienic", "dusty", "messy", "stained", "hair", "vacuum", "clean", "hygiene", "suffocating", "disgusting", "shoes", "footwear", "outside shoes", "dirty shoes", "indoors"],
    "staff": ["rude", "unhelpful", "booming", "motivation", "excellent", "good", "interesting", "love", "superb", "cool", "great", "amazing", "careless", "arrogant", "inattentive", "lazy", "misbehaving", "unprofessional", "manager", "behavior", "ignored", "ranting", "show up"],
    "AC": ["ac", "hot", "humid", "heat", "ventilation", "airflow", "cooler", "suffocating", "sweating", "stuffy", "air"],
    "overcrowding": ["crowded", "rush", "packed", "busy", "queue", "overbooked", "full", "no space", "too many", "congested"],
    "pricing": ["expensive", "costly", "overpriced", "unaffordable", "high", "rate", "charge"],
    "experience": ["music", "wonderful", "amazing", "speaker", "silent", "boring", "dull", "quiet", "vibe", "playlist", "songs", "choreography", "dance"],
    "amenities": ["water", "bottle", "empty", "dispenser", "refill", "cooler", "thirsty", "gel", "relispray", "gloves", "mats", "spray", "towel"],
    "trainer": ["instructions", "clarity", "corrections", "energy", "engaging", "motivating", "encouraging", "supportive"],
    "maintenance_safety": ["floor", "worn", "uneven", "injury", "hazard", "danger", "slip", "rectify", "repair", "safety"]
}

st.title("🏋️ ROC Actionable Insights with Center-wise Summary")

uploaded_file = st.file_uploader("Upload Gym Reviews CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', on_bad_lines='skip')

    st.success("File uploaded successfully!")
    st.write("### Raw Reviews Data", df.head())

    if 'review' not in df.columns:
        st.error("The CSV file must contain a 'review' column.")
    else:
        # Remove blank reviews
        df = df[df['review'].notna() & (df['review'].str.strip() != "")]

        # Function to extract keywords and actions
        def extract_keywords_and_action(review):
            review_lower = str(review).lower()
            actions = set()
            keywords_found = set()
            categories_found = set()

            for category, keywords in roc_action_map.items():
                for keyword in keywords:
                    if keyword in review_lower:
                        keywords_found.add(keyword)
                        actions.add(category)  # <-- ✅ changed here
                        categories_found.add(category)

            return ', '.join(sorted(keywords_found)), ', '.join(sorted(actions)) if actions else "No action", ', '.join(sorted(categories_found)) if categories_found else "No category"

        # Apply function
        df['keywords_found'], df['roc_action'], df['categories'] = zip(*df['review'].apply(extract_keywords_and_action))

        # Columns to show
        columns_to_show = ['centre_name', 'review', 'keywords_found', 'roc_action'] if 'centre_name' in df.columns else ['review', 'keywords_found', 'roc_action']

        st.write("### Analyzed Reviews with Suggested ROC Actions")
        st.dataframe(df[columns_to_show])

        # ----- Center-wise summary -----
        if 'centre_name' in df.columns:
            summary_data = []

            for center in df['centre_name'].unique():
                center_df = df[df['centre_name'] == center]
                total_reviews = center_df.shape[0]
                issues_reviews = center_df[center_df['roc_action'] != "No action"].shape[0]

                all_categories = ','.join(center_df['categories'])
                category_list = [c for c in all_categories.split(',') if c and c != 'No category']

                category_counter = Counter(category_list)
                common_issues = ', '.join([cat for cat, _ in category_counter.most_common(3)])

                # Flag if any issue category occurs >= 3 times
                recurring_flag = "✅" if any(count >= 3 for count in category_counter.values()) else "❌"

                summary_data.append({
                    'Centre Name': center,
                    'Total Reviews': total_reviews,
                    'Reviews with Issues': issues_reviews,
                    'Common Issues': common_issues,
                    'Recurring Issues': recurring_flag
                })

            summary_df = pd.DataFrame(summary_data)

            st.write("### 📊 Center-wise Summary")
            st.dataframe(summary_df)

            # Download summary
            summary_csv = summary_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Download Center-wise Summary CSV",
                data=summary_csv,
                file_name='center_summary.csv',
                mime='text/csv'
            )

        # Download analyzed reviews
        analyzed_csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="⬇️ Download Analyzed Reviews CSV",
            data=analyzed_csv,
            file_name='gym_reviews_with_actions.csv',
            mime='text/csv'
        )
else:
    st.info("Please upload a CSV file to proceed.")
