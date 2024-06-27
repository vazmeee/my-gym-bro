import streamlit as st
import pandas as pd
import random
import openai


st.set_page_config(layout="wide")

st.title('My Gym Bro')
st.header('Your virtual workout partner')

personal_info, goals, current_status = st.columns(3)

with personal_info:
    st.subheader('Bio Info', divider=True)
    GENDERS = ['Male', 'Female', 'Dont want to disclose', 'Other']

    gender = st.selectbox('Gender', options=GENDERS)
    height = st.number_input('Add your height in cm')
    weight = st.number_input('Add your weight in kgs')
    medical_history = st.text_area('Medical history')

with goals:
    st.subheader('Goals', divider=True)
    target = st.text_area('Add your target')
    timeframe = st.number_input('Add your timeframe in number of weeks')

with current_status:
    st.subheader('Current exp', divider=True)
    current_experience = st.selectbox('Current experience', ['beginner', 'intermediate', 'advanced'])
    current_routine = st.text_area('Current Routine')
    interests = st.text_input('Your interests')

submit_init = st.button('Go!')




# DF_PATH = '~/Downloads/Workout List.xlsx'
DF_PATH = 'workouts-2_2024-06-25 23:02:10.679166.parquet'

# in minutes
DEFAULT_DURATION = {
    'beginner': '30-60',
    'intermediate': '45-90',
    'advanced': '90-150'
}

HEADERS_EXCEL = [
    'name',
    'media',
    'muscles-worked-img',
    'primary-muscles-worked',
    'secondary-muscles-worked',
    'how-to',
    'commentary',
    'raw-page-text',
    'raw-page-html',
    'category',
    'difficulty',
    'rep-range',
    'sets-range',
    'equipment',
    'calories-expended-total',
    'frequency'
]

HIDDEN_COLUMNS = ['raw-page-text', 'raw-page-html']

WORKOUT_TYPE = ['chest', 'shoulder', 'bicep', 'tricep', 'leg', 'back', 'glute', 'abs', 'calves',
                'forearm forearm and grip', 'forearm extensor', 'cardio']

st.divider()

st.subheader('Build your workout')

workout_types = st.multiselect('Workout mix', WORKOUT_TYPE, max_selections=3)

if submit_init and current_experience:

    # in minutes
    def_min_duration = int(DEFAULT_DURATION[current_experience].split('-')[0])
else:
    def_min_duration = 30

workout_time = st.number_input('Duration of workout (in minutes)', min_value=def_min_duration)

df = pd.read_parquet(DF_PATH)
df = df.drop(columns=['raw-page-text', 'raw-page-html'])

workout_split = []
if current_experience == 'beginner':
    df = df[df['difficulty'] == 'beginner']
    workout_split = [100]
elif current_experience == 'intermediate':
    df = df[df['difficulty'].isin(['beginner', 'intermediate'])]
    workout_split = [70, 30]
elif current_experience == 'advanced':
    # df = df[df['difficulty'].isin(['beginner', 'intermediate', 'advanced'])]
    workout_split = [60, 30, 10]

workout_timer = 0

per_set_time = 2.5 # minutes

wo_names = []
# workouts = []

# TODO: later fix
# if len(workout_types) > 0:
#     for workout_type in workout_types:
#         wo = df[df['category']==workout_type].sample(1).reset_index().to_dict('index')[0]
#         set_range_max = int(wo['sets-range'].split('-')[1])
#         if not wo['name'] in wo_names:
#             wo_names.append(wo['name'])
#             workouts.append(wo)
#             workout_timer -= set_range_max*per_set_time
#
# else:

num_workouts = int(workout_time/7)
if len(workout_types) > 0:
    workouts = df[df['category'].isin(workout_types)].sample(num_workouts)
else:
    workouts = df.sample(num_workouts)

st.divider()
workouts = workouts.drop(columns=['media', 'muscles-worked-img', 'commentary', 'frequency']).reset_index(drop=True).sort_values(by=['category'])

st.subheader('Workout plan')
st.table(workouts)

st.divider()

st.subheader('Workout buddy chat')


muscle_groups = 'legs'
if len(workout_types) > 0:
    muscle_groups = ', '.join(workout_types)

prompt = f"""
You are at a gym. Your gender is {gender}. Your skill level is {current_experience}. 
Your goals are {target}.
You are working out on {muscle_groups} muscle groups.
This is the workout plan for today: {', '.join(workouts['name'])}
You are interested in {interests}.
You will now assume a name and have a conversation at a gym. 
Start with an introduction. Introduce yourself just once. Do not overwhelm the user with too much. a simple introduction at first. 
After the intro, talk about your workouts. 
After talking about workouts, Ask if they want to workout together.
After asking if they want to workout out together, give a suggestion about a workout. 
During the breaks of the workout, Do some small talk during the break.
You can also talk about the interests when small talking.
The conversation will start now
"""

client = openai.OpenAI(
    base_url=st.secrets["BASE_URL"],
    api_key=st.secrets["API_KEY"]
)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = st.secrets["MODEL"]

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.session_state.messages.append({"role": "user", "content": prompt})
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})


st.divider()

st.write('If you like this and are interested. [join the waitlis](mygymbro.framer.website)')
st.write('Built with ❤️ by [vazmeee](x.com/vazmeee_stfu)')
st.write('A [buildspace](https://www.instagram.com/_buildspace/) n&w project')
