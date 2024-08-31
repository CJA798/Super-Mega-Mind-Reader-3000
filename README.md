#           Super-Mega-Mind-Reader-3000
![Alt Text](https://github.com/CJA798/Super-Mega-Mind-Reader-3000/blob/ffff09888d9517a2f05e0c7d957472e5b5a27f83/img/Cover.png)

## About
### What is the project?
The Super Mega Mind Reader 3000 is a program capable of collecting and preprocessing data from an OpenBCI headset, as well as training and testing neural network models trained on such data. It is also capable of displaying a GUI that lets the user know the real-time prediction metrics of the model.

### Who's it intended for?
This project is intended primarily for undergraduate research purposes at the University of North Carolina - Asheville.

### What problem does the project solve?
The project offers an alternative approach for the real-time classification of electroencephalography (EEG) signals generated during motor imagery (MI) [1].

### How is it going to work?
The project offers the following options:
- Data:
  - Load:
    - Loads a dataset    
  - Collect:
    - Uses the OpenBCI headset and a random cue sequence to capture data 
  - Preprocess
    - Apply different preprocessing techniques to a dataset
- Model:
  - Load
    - Loads a model
  - Train
    - Trains a model using a predefined architecture
  - Test:
    - From dataset
      - Uses a test dataset to evaluate the performance of the model
    - Live
      - Starts capturing and making predictions on signal packages from the OpenBCI headset   

## References
[1]F. Mino, “Training a Convolutional Neural Network to Classify Motor Imagery EEG  Signals for Brain-Computer Interface Applications,” UNC Asheville’s Journal of Undergraduate Research, no. 9, May 2021, Accessed: Mar. 28, 2024. [Online]. Available: https://drive.google.com/file/d/1q4_OXKz2ur8ObY-T47_tPfMJrgcLzlHT/view
