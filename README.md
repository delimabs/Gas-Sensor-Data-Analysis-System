# Gas-Sensor-Data-Analysis-System (GSDAS)
The Gas Sensor Data Analysis System is an open-source graphical user interface that facilitates the analysis procedure of dynamic response-recovery curves of gas sensors. The code was written in python 3, and it uses the open-source libraries matplotlib, pandas, NumPy, and SciPy for data visualization, handling, and fitting. PyQt is the library used for the graphical elements because it offers excellent flexibility and compatibility with different operating systems. It can analyze eight samples simultaneously that share the same time data, shortening the analysis process to a couple of minutes and using the same criteria to calculate the three main properties of a gas sensor: its response, the response time, and recovery time.

This is a beta test version under a typical GNU License. 

Please, file suggestions and bug reports!

## Features

A typical response-recovery curve of a gas sensor consists of plotting the sensor signal as a function of time. Modern experimental benches in industry or academia can simultaneously record the data for several sensors during several exposure cycles, generating a significant amount of data to be analyzed. If the analysis is made manually, it can be tedious and prone to error process.

The Gas Sensor Data Analysis system can handle CSV files that contain data from up to eight samples that share the same time data table. It assumes that the first column is the time data, and all others are different channels in which the sensor signal was recorded. 

The system offers a simple tool to:

1.	Plot the data
2.	Define a region of interest
3.	Normalization for comparison
4.	Simultaneous calculation of response, response-time, and recovey-time for all channels in the data file 
5.	Power-law fitting of the response data
6.	Exporting the analysis

## System Requirements

Operating System: Windows 8, Windows 8.1, Windows 10
Processor: 1.6 GHz 
Memory: 4 GB RAM 
Hard Disk Space: 

These system requirements were set after our most recent tests.

## Installation
To intall a standalone version of this software, download the file gsdas 0.9.exe to open the installer [here](https://drive.google.com/drive/folders/1eW2FeAMugAU2CMUTQ32T6FijdTAGAont?usp=sharing)

## Testing

For testing all functionalities of the software, the file dataSample_1 is available for download.

This file contains the time table in seconds, and each column represents the electrical resistance in Ohms from four different samples. By opening up this file in File > Open > Open CSV, the user can set the column separator to Tab, number of channels to 4, time factor to 60, channel factors to 1e3. Now, the time units are minutes, and the sensor signal is electrical resistance in kOhms. These unit values could also be given by the user and preview the data table. By accepting it, the data will be plotted in the plot area. To choose the visualization parameters for this analysis, the user can leave the four channles selected, set the time interval to 310 to 650 minutes, and select the time to zero check box.

To perform a fast comparison between the samples, the user can access the normalization menu and enter 50 in the input menu. The system has now divided each column by its own value at 50 minutes. This feature is designed for fast comparison between each data table. By clicking the visualization button, the previous data set is plotted. 

By clicking the Response button in the dock menu, the user will access the response analysis menu. This dataset consists of a four-cycle exposure to NO2 of four different rGO-based sensors, exhibiting a p-type behavior towards this strong oxidizing gas. The exposure concentration is 0.5, 1, 2, and 5 ppm for each cycle, and they last 10 minutes. The recovery was set to 50 minutes. For each cycle, the user can enter the correspondent start time of exposure time, end time of exposure, and end time of recovery. 

For instance, in the first cycle, these values are 50, 60, and 110 min. For the second, 110, 120, and 170. After entering the four exposure cycles information, calculating the response parameters for each cycle, and appending each of these values to a table, the user can then plot the response, response time, and recovery time versus concentration. Finally, these values can be fitted to a power law R = aC^b, in which a and b are constants. The system will return a plot of the response data and the power-law fit for each column of the initial data set.

All data and fit information can be exported to a specific location as .dat CSV files by clicking the Export button menu in the dock widget. The system will generate “.dat” files that will use the same column separator as the initial data file. 

These files “dataSample_1 Analysis. The prefixes FIT_DATA, FIT_INFO, NORM_DATA, RESPONSE_DATA, and VIS_DATA are related fitting data, info, normalization data, response data, and visualization data. These files are available for download.

## Authors

Bruno S. de Lima, Weverton A. S. Silva, Valmor R. Mastelaro, Amadou L. Ndiaye, Jérôme Brunet


## Acknowledgments

This work was based upon financial support from the Sao Paulo Research Foundation. 
