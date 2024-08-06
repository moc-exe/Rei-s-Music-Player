import PySimpleGUI as sg
import mutagen.mp3 as muta
import os
import pygame
import re
import time


# method for extracting the audio track length
def getStrTracklength(file_path):
    # load the MP3 file
    audio = muta.MP3(file_path)
    
    # get the length of the MP3 file in seconds
    lengthInSeconds = audio.info.length
    
    return time.strftime("%M:%S", time.gmtime(lengthInSeconds))

# method for retrieving filepaths and filenames for a given folder
def getMP3files(folder_path):
    mp3_files = []
    mp3_names = []
    for root, dirs, files in os.walk(folder_path): 
        
        # os.walk will return a 3-tuple with root as current folder, dirs as a list of all dirs in the current folder
        # files in the current directory


        for file in files:
            if file.endswith('.mp3'):
                mp3_names.append(file)
                mp3_files.append(os.path.join(root, file))
    return (mp3_files, mp3_names)

def getStrTrackCurrTime():
    
    pos = pygame.mixer.music.get_pos()
    return time.strftime("%M:%S", time.gmtime(pos / 1000))

def getSecTrackLen(file_path):
    
    return muta.MP3(file_path).info.length



pygame.mixer.init()
pygame.mixer.music.set_volume(0.7)

# defining custom theme, creating basic layout #8ba3a8
custom_window_theme= {
    'BACKGROUND': '#465178',
    'TEXT': '#FFB067',
    'INPUT': '#C8C4C1',
    'TEXT_INPUT': '#000000',
    'SCROLL': '#c7e78b',
    'BUTTON': ('#FFB067', '#002134'),
    'PROGRESS': ('#FFB067', '#002134'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0}
sg.theme_add_new("custom1", custom_window_theme)
sg.theme("custom1")

col11_layout = [[sg.Image(filename = "./img/rei_round.png", subsample=3)]]
col12_layout = [[sg.Image(filename="./img/music-player-logo.png")]]
                
layout = [

    [sg.Column(col11_layout, element_justification='center'), sg.Column(col12_layout)],
    [sg.Button('Prev'), sg.Button('Play'), sg.Button('Pause'), sg.Button('Next'), sg.Button("Stop"), sg.Button("Exit"), sg.In(size=(25,1), enable_events=True ,key='-BROWSE-', visible=False), sg.FolderBrowse()],
    [sg.StatusBar("Select a folder", key="-STATUS_BAR-")]

]

window = sg.Window("Rei's Music Player", layout, finalize=True, icon='./img/ico64.ico')

# needa implement that stuff stillz
autoplay = True
totalTrackLen = None
mp3files = None
mp3filenames = None
currentTrackPath = None
currentTrackIndex = None
isPlaying = False
trackStarted = False


while True:
    event, values = window.read(timeout=100)
    
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

    if isPlaying: # progress bar and time updates are here
        window['-TRACK_TIME-'].update(f'Time: {getStrTrackCurrTime()} / {getStrTracklength(currentTrackPath)}')
        window['-CURRENT_SONG-'].update(f'Track: {mp3filenames[currentTrackIndex]}'[:-4])
        window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)} {getStrTrackCurrTime()} / {getStrTracklength(currentTrackPath)}')
        window['-PROGRESS-'].update(current_count = int((pygame.mixer.music.get_pos()//1000)*100 / (getSecTrackLen(currentTrackPath))))
  
    if event == '-BROWSE-':   # folder and playlist selection logic
        
        folder = values['-BROWSE-']
        
        if folder:

            mp3files, mp3filenames = getMP3files(folder)
            
            if mp3files:    #if mp3 files were found

                tableData = []
                
                for i in range(len(mp3filenames)):
                    tableData.append([i + 1, mp3filenames[i], getStrTracklength(mp3files[i])])
                
                window.close()
                
                col11_layout = [[sg.Image(filename = "./img/rei_round.png", subsample=3)]]
                col12_layout = [[sg.Image(filename="./img/music-player-logo.png"),],
                                [sg.Text(key = '-CURRENT_SONG-', font = 'Monospace 12 bold', text_color = '#FFB067', size = (20, 2))],
                                [sg.Text(key = '-TRACK_TIME-', font = 'Monospace 12 bold', text_color = '#FFB067', size = (20, 2))]]

                newLayout = [

                [sg.Push(),sg.Column(col11_layout, element_justification='center'), sg.Column(col12_layout, element_justification='center'), sg.Push()],
                [   
                    sg.Push(),
                    sg.Button('Prev'), 
                    sg.Button('Play'), 
                    sg.Button('Pause'), 
                    sg.Button('Next'), 
                    sg.Button("Stop"), 
                    sg.Button("Exit"), 
                    sg.In(size=(25,1), enable_events=True ,key='-BROWSE-', visible=False), 
                    sg.FolderBrowse(), 
                    sg.Push() 
                    
                ],

                [sg.Push(), sg.ProgressBar(100, size=(45, 8), key = "-PROGRESS-", pad = (5,5)), sg.Push()],

                [   
                    sg.Text('Volume', font = 'Monospace 12 bold', key = '-VOLUME_LABEL-'),
                    sg.Slider(
                            range=(0, 100), 
                                orientation='h', 
                                key='-VOLUME-', 
                                enable_events=True, 
                                background_color='#465178',
                                trough_color='#FFB067', 
                                size=(20, 10),
                                border_width=0, 
                                disable_number_display=True,
                                default_value = 70
                                ),
                    sg.Text('70%', font = 'Monospace 11', key = '-VOLUME_PERCENTAGE-'),
                    sg.Push()
                ],
                [sg.Text('Your Playlist', font = 'Monospace 14 bold', text_color = '#FFB067')],
                [sg.Table(
                            values = tableData,
                            headings=['Index', 'Track name', 'Total Length'],
                            max_col_width=35,
                            auto_size_columns=True,
                            display_row_numbers=False,
                            justification='right',
                            num_rows=min(len(tableData), 8),
                            key='-PLAYLIST-',
                            row_height=35,
                            enable_events=True)],
                [sg.StatusBar("No Track Playing Just Yet", key="-STATUS_BAR-", size=(50,1))],
                ]

                window = sg.Window("Rei's Music Player", newLayout, finalize=True, icon='./img/ico64.ico')

                
            else:   #if no mp3 files encountered in the folder chosen

                window.close()
                
                col11_layout = [[sg.Image(filename = "./img/rei_round.png", subsample=3)]]
                col12_layout = [[sg.Image(filename="./img/music-player-logo.png")],
                                [sg.Text(key = '-CURRENT_SONG-', font = 'Monospace 12 bold', text_color = '#FFB067', size = (20, 2))],
                                [sg.Text(key = '-TRACK_TIME-', font = 'Monospace 12 bold', text_color = '#FFB067', size = (20, 2))]]

                newLayout = [

                [sg.Push(), sg.Column(col11_layout, element_justification='center'), sg.Column(col12_layout), sg.Push()],
                [
                    sg.Push(),
                    sg.Button('Prev', disabled=True), 
                    sg.Button('Play', disabled=True), 
                    sg.Button('Pause', disabled=True), 
                    sg.Button('Next', disabled = True), 
                    sg.Button("Stop", disabled = True), 
                    sg.Button("Exit"), 
                    sg.In(size=(25,1), enable_events=True ,key='-BROWSE-', visible=False), 
                    sg.FolderBrowse(),
                    sg.Push() 
                    
                ],
                [sg.Push(), sg.ProgressBar(100, size=(45, 5), key = "-PROGRESS-"), sg.Text(key = '-TRACK_TIME-'),sg.Push()],
                [sg.Text('Your Playlist: Empty', font = 'Monospace 14 bold', text_color = '#FFB067')],
                [sg.StatusBar("No Track Playing Just Yet", key="-STATUS_BAR-", size=(50,1))]
                ]
                window = sg.Window("Rei's Music Player", newLayout, finalize=True, icon='./img/ico64.ico')
                window['-STATUS_BAR-'].update("Folder chosen does not have any mp3 files")

    if event == '-PLAYLIST-': # table track selection logic here

        
        currentTrackIndex = (values['-PLAYLIST-'][0]) if values['-PLAYLIST-'] else None
        
        if currentTrackIndex or currentTrackIndex == 0:
            currentTrackPath = mp3files[currentTrackIndex]
            pygame.mixer.music.load(currentTrackPath)
            pygame.mixer.music.play()
            isPlaying = True
            trackStarted = True
            window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')

    if event == '-VOLUME-': # slider and volume adjustment logic here
        
        pygame.mixer.music.set_volume(values['-VOLUME-'] / 100.0)
        window['-VOLUME_PERCENTAGE-'].update(f'{int(values['-VOLUME-'])}%')

    if event == "Play":
        
        if not mp3files:
            window['-STATUS_BAR-'].update('No tracks')
        

        elif mp3files and currentTrackIndex is None:
            currentTrackIndex = 0
            currentTrackPath = mp3files[currentTrackIndex]
            pygame.mixer.music.load(currentTrackPath)
            pygame.mixer.music.play()
            trackStarted = True
            isPlaying = True
            window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')
            window['-PLAYLIST-'].update(select_rows = [currentTrackIndex])

        elif mp3files and not isPlaying and currentTrackIndex is not None and trackStarted:
            pygame.mixer.music.unpause()
            isPlaying = True
            window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')

        elif mp3files and not isPlaying and currentTrackIndex is not None:
            pygame.mixer.music.play()
            isPlaying = True
            trackStarted = True
            window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')
            
    if event == "Pause":

        if not mp3files or currentTrackIndex is None or currentTrackPath is None:
            continue

        elif isPlaying:

            pygame.mixer.music.pause()
            isPlaying = False
            window['-STATUS_BAR-'].update('Paused')
        
        else:
            if mp3files and not isPlaying and currentTrackIndex is not None:
                pygame.mixer.music.unpause()
                isPlaying = True
                window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')

    if event == "Stop":
       
        if mp3files is None or currentTrackPath is None:
            window['-STATUS_BAR-'].update('No tracks')
            continue
       
        elif currentTrackPath and isPlaying:
            currentTrackIndex = 0
            pygame.mixer.music.stop()
            isPlaying = False
            trackStarted = False
       
        elif currentTrackPath and not isPlaying:
            currentTrackIndex = 0
            pygame.mixer.music.stop()
            trackStarted = False
    
        window['-STATUS_BAR-'].update('Stopped')
        window['-PLAYLIST-'].update(select_rows = [])
        window['-TRACK_TIME-'].update(" ")
        window['-CURRENT_SONG-'].update(' ')
        window['-PROGRESS-'].update(current_count = 0)

    if event == "Next":

        if not mp3files or currentTrackIndex is None:
            window['-STATUS_BAR-'].update('No tracks')
        
        currentTrackIndex += 1
        if currentTrackIndex >= len(mp3files):
            currentTrackIndex = 0
        currentTrackPath = mp3files[currentTrackIndex]
        pygame.mixer.music.load(currentTrackPath)
        pygame.mixer.music.play()
        isPlaying = True
        trackStarted = True
        window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')
        window['-PLAYLIST-'].update(select_rows = [currentTrackIndex])
    
    if event == 'Prev':
        if not mp3files or currentTrackIndex is None:
            window['-STATUS_BAR-'].update('No tracks')

        currentTrackIndex -= 1
        if currentTrackIndex < 0:
            currentTrackIndex = (len(mp3files) - 1)
        currentTrackPath = mp3files[currentTrackIndex]
        pygame.mixer.music.load(currentTrackPath)
        pygame.mixer.music.play()
        isPlaying = True
        trackStarted = True
        window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')
        window['-PLAYLIST-'].update(select_rows = [currentTrackIndex])

    # defo needa implement loop and autoplay properly for now we assume it's = True
    if isPlaying and not pygame.mixer.music.get_busy(): # autoplay logic is all here for now ..?
        currentTrackIndex += 1
        if currentTrackIndex >= len(mp3files):
            currentTrackIndex = 0
        currentTrackPath = mp3files[currentTrackIndex]
        pygame.mixer.music.load(currentTrackPath)
        pygame.mixer.music.play()
        trackStarted = True
        window['-STATUS_BAR-'].update(f'Playing {os.path.basename(currentTrackPath)}')
        window['-PLAYLIST-'].update(select_rows = [currentTrackIndex])


window.close()
pygame.quit()


