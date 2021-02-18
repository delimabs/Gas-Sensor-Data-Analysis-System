# Gas-Sensor-Data-Analysis-System (GSDAS)
The Gas Sensor Data Analysis System is an open-source graphical user interface that facilitates the analysis procedure of dynamic response-recovery curves of gas sensors. The code was written in python 3, and it uses the open-source libraries matplotlib, pandas, NumPy, and SciPy for data visualization, handling, and fitting. PyQt is the library used for the graphical elements because it offers excellent flexibility and compatibility with different operating systems. It can analyze up to eight samples simultaneously that share the same time data, shortening the analysis process to a couple of minutes and using the same criteria to calculate the three main properties of a gas sensor: its response, the response time, and recovery time.

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

For testing all functionalities of the software, the files dataSample_1 and dataSameple_2 are available for download.

### dataSample_1

This dataset corresponds to four different rGO-based sensors whose electrical resistance was recorded by controlled exposures of NO<sub>2</sub>, between 0.5 and 5 ppm. Each exposure cycle lasted 10 min and the recovery 50 min. For more information on the experimental details on this measurement, please, read the Experimental Info on the dataSample_1 file.

### dataSample_2

This dataset corresponds to a stability test carried out on two ZnO-based sensors upon controlled O<sub>3</sub> exposure between 50 and 500 ppb during one month. Channels 1, 2, and 3 are the data from one sensor measured on three different weeks, while data from channels 4, 5, and 6 are the data from another similar sample measured at the same three weeks.

Each exposure cycle was set to 15 min and the recovery to 60 min. For more information on the experimental details on this measurement, please, read the Experimental Info on the dataSample_2 file.

## Authors

Bruno S. de Lima, Weverton A. S. Silva, Amadou L. Ndiaye, Valmor R. Mastelaro, and Jérôme Brunet


## Acknowledgments

This work was based upon financial support from the Sao Paulo Research Foundation. 
