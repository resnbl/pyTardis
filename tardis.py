"""
Main TARDIS script - see README.MD for an overview of how and why this exists.
"""
__version__ = '1.0.0'

from pathlib import Path
import base64
import PySimpleGUI as sg
from tardis_controller import TardisController, IDLE_TITLE, MAX_VOL, INIT_VOL
from animated_image import AnimatedImage
# from timed_print import elapsed_print as eprint   # pick one
eprint = print                                      # or the other

sg.theme('Tan Blue')
THE_FONT = ('Gill Sans', 17)    # ('Lato', 15) is nice, also    # ('Any', 15) # noqa

# Where all the pretty pictures are:
IMAGES = Path(__file__).parent / 'images'
TARDIS_ICON = base64.b64encode(open(IMAGES / 'tardis_icon.png', 'rb').read())
STATIC_TARDIS_BEACON = str(IMAGES / 'tardis_beacon.png')
STATIC_TARDIS_BOX = str(IMAGES / 'tardis_box.png')
PREV_BTN = str(IMAGES / 'btn_prev_ani.png')
NEXT_BTN = str(IMAGES / 'btn_next_ani.png')
PLAY_BTN = str(IMAGES / 'btn_play.png')
PAUSE_BTN = str(IMAGES / 'btn_stop.png')
EXIT_BTN = str(IMAGES / 'btn_power_ani.png')    # 'btn_stop_ani.png')

# and all the lovely tunes...
AUDIO = Path(__file__).parent / 'audio'

# widget keys
LIST_KEY = '-LIST-'
PLAY_KEY = '-PLAY-'
PREV_KEY = '-PREV-'
NEXT_KEY = '-NEXT-'
DEMO_KEY = '-DEMO-'
VOL_KEY = '-VOL-'
PB_KEY = '-PB-'
BEACON_KEY = '-BEACON-'
BOX_KEY = '-BOX-'
EXIT_KEY = '-EXIT-'
TIMEOUT_KEY = sg.TIMEOUT_KEY

# Customize some widgets
BTN_COLOR = (sg.theme_text_element_background_color(), sg.theme_text_element_background_color())
PBAR_COLOR = (sg.theme_button_color()[1], sg.theme_background_color())

# Padding to get images next to each other vertically
DEF_LR, DEF_TB = 5, 3           # default sg.Image padding
PAD_NO_BTM = (DEF_LR, (DEF_TB, 0))
PAD_NO_TOP = (DEF_LR, (0, DEF_TB))
# PAD_NO_VERT = (DEF_LR, 0)     # for the "complete-ists"


def make_layout(names: list[str]) -> list[list]:
    """Define the GUI layout as a single row with 2 columns: the TARDIS beacon/box and the controls"""
    img_bg_color = sg.theme_background_color()      # for transparent images

    pics = sg.Column([
        [sg.Image(filename=STATIC_TARDIS_BEACON, key=BEACON_KEY, pad=PAD_NO_BTM)],
        [sg.Image(filename=STATIC_TARDIS_BOX, key=BOX_KEY, pad=PAD_NO_TOP)]
    ])

    controls = sg.Column([
        [sg.Text('Track List:')],
        [sg.Listbox(names, default_values=[names[0]], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    size=(25, 5), key=LIST_KEY, enable_events=True)],
        # [sg.Text('')],
        [sg.Checkbox('Demo Mode', key=DEMO_KEY, enable_events=True)],
        [sg.Text('Volume', pad=PAD_NO_BTM)],
        [sg.Slider((0, MAX_VOL), default_value=INIT_VOL,
                   resolution=1, tick_interval=MAX_VOL, enable_events=True,
                   orientation='h', key=VOL_KEY, expand_x=True, pad=PAD_NO_TOP)],
        [sg.Text('')],

        # PREV/NEXT buttons are animated images
        [sg.Image(filename=PREV_BTN, key=PREV_KEY, background_color=img_bg_color, enable_events=True),
         sg.Push(),
         # PLAY/PAUSE can't be animated since it immediately toggles when clicked
         sg.Button('', key=PLAY_KEY, image_filename=PLAY_BTN, button_color=BTN_COLOR, border_width=0),
         sg.Push(),
         sg.Image(filename=NEXT_BTN, key=NEXT_KEY, background_color=img_bg_color, enable_events=True)
         ],

        [sg.Text('')],
        [sg.ProgressBar(max_value=100, size=(10, 20), expand_x=True, orientation='h', border_width=2,
                        key=PB_KEY, bar_color=PBAR_COLOR)],
        [sg.Text('')],
        [sg.Push(),
         sg.Image(filename=EXIT_BTN, key=EXIT_KEY, background_color=img_bg_color, enable_events=True),
         sg.Push()]
    ])

    return [[pics, controls]]


def main():
    """Main program with event loop"""
    tc = TardisController(AUDIO, IMAGES)
    # init our window
    layout = make_layout(tc.titles)
    window = sg.Window(title=IDLE_TITLE, layout=layout, font=THE_FONT, icon=TARDIS_ICON, finalize=True)
    track_list = window[LIST_KEY]
    play_btn = window[PLAY_KEY]
    prog_bar = window[PB_KEY]
    progress = 0
    tc.set_images(window[BEACON_KEY], window[BOX_KEY])
    # Demo our fancy animated buttons
    ani_next = AnimatedImage(window[NEXT_KEY], NEXT_BTN)
    ani_prev = AnimatedImage(window[PREV_KEY], PREV_BTN)

    is_playing = False          # may lead/lag actual player status
    is_demo_mode = False

    while True:
        event, values = window.read(10)     # short t/o for smoother animations, but not too short!

        if event == TIMEOUT_KEY:        # check the most frequent event first
            if is_playing:                  # it was playing...
                if tc.is_playing:           # but is it still?
                    tc.run_effects()        # yes: continue animations
                    if progress != tc.progress:
                        progress = tc.progress
                        prog_bar.update(current_count=progress)
                else:   # track ended since last event loop; queue STOP button
                    window.write_event_value(PLAY_KEY, None)

            elif is_demo_mode:          # not playing: auto-play next track?
                tc.select_next()
                is_playing = False
                window.write_event_value(PLAY_KEY, None)    # queue PLAY button

            ani_next.run()
            ani_prev.run()

        elif event == PLAY_KEY:
            if is_playing:      # then stop it!
                tc.stop()
                window.set_title(IDLE_TITLE)
                play_btn.update(image_filename=PLAY_BTN)    # toggle stop -> play
                prog_bar.update(current_count=0)
                is_playing = False
            else:               # then get started!
                title_duration = tc.play()
                window.set_title(title_duration)
                eprint(title_duration)
                scroll_to = max(0, tc.track_index - 2)      # center selection (unless at #0 or #1)
                track_list.update(set_to_index=tc.track_index, scroll_to_index=scroll_to)
                play_btn.update(image_filename=PAUSE_BTN)   # toggle play -> stop
                progress = 0
                prog_bar.update(current_count=progress)
                is_playing = True

        elif event == LIST_KEY:
            tc.select_title(values[LIST_KEY][0])
            is_playing = False
            window.write_event_value(PLAY_KEY, None)        # queue PLAY button
        elif event == PREV_KEY:
            tc.select_prev()
            ani_prev.start()
            is_playing = False
            window.write_event_value(PLAY_KEY, None)        # queue PLAY button
        elif event == NEXT_KEY:
            tc.select_next()
            ani_next.start()
            is_playing = False
            window.write_event_value(PLAY_KEY, None)        # queue PLAY button

        elif event == VOL_KEY:
            tc.set_volume(values[VOL_KEY])

        elif event == DEMO_KEY:     # toggle "play all" mode
            is_demo_mode = values[DEMO_KEY]
            if is_demo_mode and not is_playing:
                window.write_event_value(PLAY_KEY, None)    # queue PLAY button

        elif event == sg.WINDOW_CLOSED or event == EXIT_KEY or event is None:
            tc.stop()
            break
        else:
            eprint(f'Unexpected event: {event} value: {values.get(event)}')
    # end event loop

    if event == EXIT_KEY:       # only if leaving via EXIT button
        # But wait! We've got a big finish! (flash animated buttons)
        ani_next.start()
        ani_prev.start()
        ani_exit = AnimatedImage(window[EXIT_KEY], EXIT_BTN).start()
        while window.read(10)[0] == TIMEOUT_KEY:
            # These animations all have loop==1, so this doesn't last long
            if not(ani_exit.running or ani_next.running or ani_prev.running):
                break   # now we can die...
            ani_next.run()
            ani_prev.run()
            ani_exit.run()

    window.close()
    # print("Time's up!")


if __name__ == '__main__':
    # print('Tardis', __version__)
    main()
