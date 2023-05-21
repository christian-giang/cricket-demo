import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi
from datetime import datetime
import time
import base64

try:
    import pickle5 as pickle
except ImportError:
    import pickle

# *********** DISABLE HAMBURGER MENU **************

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# *********** DEFINITION OF FUNCTIONS **************



# Function for plotting fighters clusters by round 

def plot_clusters(round):

	fig = plt.figure(figsize=(3,3))
	ax = plt.subplot(polar="True")

	categories = ['Distance', 'Clinch', 'Ground','Grappling', 'Aggressiveness']
	n_cats = len(categories)

	df_fighter_tmp = df_fighter_fight[df_fighter_fight['Rd']==round]
	df_opp_tmp = df_opp[df_opp['Rd']==round]

	#st.dataframe(df_fighter_tmp)

	values = [df_fighter_tmp['ClusterDST'].values,df_fighter_tmp['ClusterCLC'].values,df_fighter_tmp['ClusterGRD'].values,df_fighter_tmp['ClusterGRAP'].values,df_fighter_tmp['ClusterAGGR'].values]
	values +=values[:1]

	values_opp = [df_opp_tmp['ClusterDST'].values,df_opp_tmp['ClusterCLC'].values,df_opp_tmp['ClusterGRD'].values,df_opp_tmp['ClusterGRAP'].values,df_opp_tmp['ClusterAGGR'].values]
	values_opp +=values_opp[:1]


	angles = [n/float(n_cats) * 2 * pi for n in range(n_cats)]
	angles +=angles[:1]

	plt.polar(angles,values, marker='s', color='crimson', label=df_fighter_tmp['FighterName'].values[0])
	plt.fill(angles, values, alpha=0.3 , color='crimson')
	plt.polar(angles,values_opp, marker='s' , color='dimgrey', label=df_opp_tmp['FighterName'].values[0])
	plt.fill(angles, values_opp, alpha=0.3, color='silver')
	plt.xticks(angles[:-1], categories)
	plt.title("ROUND " + str(round), loc='left', fontweight="bold", color="white")
	if round==2:
		plt.legend(bbox_to_anchor =(0.8, -0.15), ncol=1)

	ax.set_rlabel_position(0)

	ax.xaxis.label.set_color('white')
	ax.tick_params(axis='x', colors='white')
	ax.yaxis.label.set_color('white')
	ax.tick_params(axis='y', colors='white')

	plt.yticks([0,1,2], color='grey', size=10)
	fig.patch.set_alpha(0)


	return fig


# Function for displaying predictions

def list_preds(df_pred, df_accuracy, pred_choice):

	for index, row in df_pred.iterrows(): 

		transaction = row['TxID']
		bsv_link = 'https://whatsonchain.com/tx/' + transaction

		if ((row['RC_nrecords'] > df_accuracy.iloc[0,7]-1) & (row['BC_nrecords'] > df_accuracy.iloc[0,7]-1) & (abs(row[odds_fighter1] - row[odds_fighter2]) > df_accuracy.iloc[0,6])):
			display_odds1 = str(row[odds_fighter1]) + ' (*)'
			display_odds2 = str(row[odds_fighter2]) + ' (*)'		
		else:
			display_odds1 = str(row[odds_fighter1])
			display_odds2 = str(row[odds_fighter2])	

		display_name1 = row['RC'] 
		display_name2 = row['BC'] 

		if row['PredictedWinner'] == row['RC']:
			display_name1 = display_name1 + ' (P)'
		elif row['PredictedWinner'] == row['BC']:
			display_name2 = display_name2 + ' (P)'

		if pred_choice =='Past fights':
			if row['Winner'] == row['RC']:
				display_name1 = display_name1 + ' (W)'
			elif row['Winner']== row['BC']:
				display_name2 = display_name2 + ' (W)'
			elif row['Winner']== 'Draw':
					display_name1 = display_name1 + ' (D)'
					display_name2 = display_name2 + ' (D)'
			else:
				display_name1 = display_name1 + ' (N/A)'
				display_name2 = display_name2 + ' (N/A)'	

	
		col1, col2, col3 = st.columns(3)
		col1.markdown("<p style='text-align: center;'>"+display_name1+"</p>", unsafe_allow_html=True)
		col2.markdown("<p style='text-align: center;'>"+display_name2+"</p>", unsafe_allow_html=True)

		if row[odds_fighter1]<0: #If no predictions are available
			col1.markdown("<p style='text-align: center; color:grey;'> N/A</p>", unsafe_allow_html=True)
			col2.markdown("<p style='text-align: center; color:grey;'> N/A</p>", unsafe_allow_html=True)
		else:
			if row['PredictedWinner'] == row['RC']:
				col1.markdown("<p style='text-align: center; color:green;'>"+ display_odds1 +"</p>", unsafe_allow_html=True)
				col2.markdown("<p style='text-align: center; color:red;'>"+display_odds2 +"</p>", unsafe_allow_html=True)
			else:
				col1.markdown("<p style='text-align: center; color:red;'>"+display_odds1 +"</p>", unsafe_allow_html=True)
				col2.markdown("<p style='text-align: center; color:green;'>"+display_odds2 +"</p>", unsafe_allow_html=True)

		col3.markdown("<p style='text-align: center; font-style:italic;'>"+row['Division']+"</p>", unsafe_allow_html=True)

		if row[odds_fighter1]<0: #If no predictions are available
			col3.markdown("<p style='text-align: center; color:grey;'> N/A </p>", unsafe_allow_html=True)
		else:	
			col3.markdown("<p style='text-align: center;'> <a align='center' href='"+ bsv_link +"'>BSV record </a></p>", unsafe_allow_html=True)	
		col3.markdown("<p style='text-align: center;'> <br /> </p>", unsafe_allow_html=True)	

# ***********************************************


# ********** PASSWORD CHECK *******************
if 'unlocked' not in st.session_state:
    st.session_state['unlocked'] = False

correct_pass = "UFC-P!2022"

if st.session_state['unlocked'] == False:
	text_input_container1 = st.empty()
	text_input_container2 = st.empty()
	text_input_container3 = st.empty()


	text_input_container1.image("redciq-copy.png", width=175)
	text_input_container2.markdown("Please enter the access code to enter your private area.", unsafe_allow_html=True)	
	password = text_input_container3.text_input("Access code", type="password")

	if password == correct_pass:
		st.session_state['unlocked'] = True
		text_input_container1.empty()
		text_input_container2.empty()
		text_input_container3.empty()
	elif password =='':
		text_input_container4 = st.empty()
	else:
		st.error('The password you entered is wrong.')



if st.session_state['unlocked'] == True:

	# ********** SIDEBAR ELEMENTS *******************

	st.sidebar.image("redciq-copy.png", width=175)


	st.sidebar.markdown("###### The practice summary provides an overview with the most important metrics for the session. The analysis by run option provides an interactive tool to visualize each bowl and bat of the session seperately.")

	choice_subpage = st.sidebar.radio(label="", options=('Practice summary', 'Analysis by run'))


	if choice_subpage == 'Practice summary':
		subpage = 'pred'
	elif choice_subpage == 'Analysis by run':
		subpage = 'cvdemo'




	#*************************************************




	#*************** MAIN PAGE ELEMENTS **************
	if subpage== 'pred':
		col1, col2 = st.columns(2)	
		col1.image("pcb_logo.png", width=75)
		col2.markdown("<h4 style='text-align: right; color:white;'> User profile: PCB</h4>", unsafe_allow_html=True)
	
		st.markdown("""---""") 

		st.markdown("<h4 style='text-align: center; color:white;'> Pakistan Cricket Nets Session (April 09, 2023)</h4>", unsafe_allow_html=True)
		st.markdown("<h5 style='text-align: center; color:white;'> Practice summary </h4>", unsafe_allow_html=True)
		
		st.markdown("""---""")

		st.markdown("<h5 style='text-align: left; color:white;'> Bowling and batting heatmap </h4>", unsafe_allow_html=True)

		st.image("summary_heatmap.jpg")

		st.info('The visualization above depicts a heatmap of all bowled and batted balls during the practice session. The blue dots depict all the bouncing points, the green points depict the hitting point by the batsman and the red points missed bats. On the left, projections of these points for both the pitch (aerial view) and the batting area (frontal view) are shown. The different shades of green depict the different bouncing areas (Yorker, Full, Good, Short)', icon="ℹ️")


		st.markdown("""---""")
		st.markdown("<h5 style='text-align: left; color:white;'> Summary statistics </h4>", unsafe_allow_html=True)

		df_logs = pd.read_excel('data.xlsx')


		col1, col2, col3 = st.columns(3)
		col1.metric("Total runs", len(df_logs), )
		col2.metric("Bowls from left / right", str(len(df_logs[df_logs['Bowl from'] == 'Left'])) + "/" + str(len(df_logs[df_logs['Bowl from'] == 'Right'])) )
		col3.metric("Good length bowls", str(int(len(df_logs[df_logs['Bounce area'] == 'Good length'])/len(df_logs)*100))+"%")

		col1.metric("Min. speed (km/h)", str("{:.2f}".format(min(df_logs['Speed']))))
		col2.metric("Max. speed (km/h)", str("{:.2f}".format(max(df_logs['Speed']))))
		col3.metric("Bats hit/missed", str(len(df_logs[df_logs['Result'] == 'Hit'])) + "/" + str(len(df_logs[df_logs['Result'] == 'Miss'])))
			

		st.markdown("""---""")
		st.markdown("<h5 style='text-align: left; color:white;'> Table with all runs </h4>", unsafe_allow_html=True)

		st.dataframe(df_logs, height = (len(df_logs) + 1) * 35 + 3)

	elif subpage == 'cvdemo':

		col1, col2 = st.columns(2)	
		col1.image("pcb_logo.png", width=75)
		col2.markdown("<h4 style='text-align: right; color:white;'> User profile: PCB</h4>", unsafe_allow_html=True)
	
		st.markdown("""---""") 

		st.markdown("<h4 style='text-align: center; color:white;'> Pakistan Cricket Nets Session (April 09, 2023)</h4>", unsafe_allow_html=True)
		st.markdown("<h5 style='text-align: center; color:white;'> Analysis by run</h5>", unsafe_allow_html=True)
		st.markdown("""---""") 

		st.info('Below you can select each bowl / bat  executed during the practice session. To visualize a run select the corresponding Run_ID in the dropdown menu below. Depending on the internet connection, it may take up to a few seconds to load the scene. You can sort the table by attributes by clicking on the corresponding header in the table.', icon="ℹ️")
		st.markdown("""---""") 

		df_logs = pd.read_excel('data.xlsx')

		list_actions = ['']
		list_actions = list_actions + df_logs['Run_ID'].tolist()

		st.dataframe(df_logs, height=200)

		col1, col2 = st.columns([1,2])

		with col1:
			selected_action = st.selectbox("Select a run ID to display the run:", list_actions)

			
		if selected_action !='': 
			file_ = open("selected_frames/"+str(selected_action)+".gif", "rb")
			contents = file_.read()
			data_url = base64.b64encode(contents).decode("utf-8")
			file_.close()

			st.markdown(f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">', unsafe_allow_html=True)

