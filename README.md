# Renewable_energy
An analysis of energy statistics to asses the impact of renewables

This project will use Python, Jupyter Notebook, Pandas, Matplotlib, Plotly and Dash to create visualizations about US energy trends in a 
variety of sectors(wind, solar, hydro, etc.) Plotly visualizations do not show on github so to see these you have to download the Plotly package (with conda use conda install -c plotly plotly=4.5.4 or with pip use pip install plotly==4.5.4) and the repo and open them locally. The UI is built on the Dash framework and can be installed via (pip install dash==1.11.0.) Pandas, Matplotlib, Jupyter Notebook and SQLite3 are included in the anaconda package but would need to be installed as well if you don't have Anaconda. 

The idea is to assess the progress of renewable energy in the US. My original dataset by country was 123MB which is over Github's file size limit so I had to select solely US statistics and write my own customized CSV. This dataset covers 1990-2014. I've also brought in a by state dataset which covers 1990-2018 though the only visualization that shows by year is of Ky Renewables. I'm doing breakdowns by state via plotly choropleths for 2018. These can all be found on the iPython Notebook though several are also accessible via the UI. The front end interface where different statistical categories can be selected via drop down menus to show different visualizations. This is accomplished using HTML, CSS and the Python framework Dash. 

To run the UI from a console navigate into the directory containing the files and use python Dash_UI.py. The iPython Notebook must be viewed from Jupyter Notebooks. 
