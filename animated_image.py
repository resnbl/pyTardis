"""
Support for animated PNG images (.png) in PySimpleGUI.Image widgets.

Like PSG, these animations perform their own timing without using time.sleep().
You do need to call the run() method in your event loop as well as perform
a Window.read(nnn) or Window.refresh() to drive the display changes.

Unlike PSG, this class requires the PIL.Image module in order to read additional
metadata beyond what tkinter.PhotoImage provides.

It also supports:
    Animated PNG files ("APNG"). Although GIF images are supported, the
    PIL.Image package is known to have problems with some GIF files,
    especially if they are transparent images.

    Uses the durations assigned to each frame from the file (GIF/APNG)

    Stops animation when the file's loop count is reached (0 ==> infinite looping)

    Skips the optional "default image" first frame (APNG)

The optional use of the first frame as a "default image" is a feature of APNG
instended to specify a static image displayed when the animation is not running.
If present, this frame is to be skipped during the animation loop.
This is useful mainly for non-infinite-loop animations,
like emulating a button's click with an image.
"""
from pathlib import Path
import time
import PySimpleGUI as sg
from PIL import Image, ImageSequence, ImageTk


def millis() -> int:
    """Fetch current time in milliseconds"""
    return time.time_ns() // 1000000


class AnimatedImage:
    def __init__(self, image: sg.Image, filename: Path | str = None, stats=False):
        """
        Initialization:
        :param image: PSG.Image to be animated (must have finalized the Window beforehand)
        :param filename: path to .png file
        """
        self.pic = image
        self.save_image = self.pic.Widget.image         # noqa # save existing image
        self.frames: list[ImageTk.PhotoImage] = []      # frame images
        self.durations: list[int] = []                  # frame durations
        self.frame_cnt = 0
        self.has_default = False
        self.curr_frame = 0
        self.loop = 0
        self.curr_loop = 0
        self.timer = 0
        self.running = False
        self.fps_timer = 0
        self.fps_cnt = 0
        self.name = ''
        self.stats = stats

        if filename:
            self.load(filename)     # load the image file

    def load(self, filename: Path | str) -> 'AnimatedImage':
        """
        (Re-)load an animated .png file for display
        :param filename: path to .png file
        """
        if self.running:
            self.stop()

        if isinstance(filename, str):
            filename = Path(filename)
        if self.name == filename.stem:      # same file?
            return self
        if not filename.exists():
            raise FileNotFoundError('AnimatedImage file not found:', filename)

        self.frames.clear()
        self.durations.clear()
        with Image.open(filename) as img:
            self.loop = img.info.get('loop', 0)
            for frame in ImageSequence.Iterator(img):
                self.frames.append(ImageTk.PhotoImage(frame))
                self.durations.append(int(frame.info.get('duration', 0)))

        self.frame_cnt = len(self.frames)
        if self.frame_cnt == 1:
            print(f'Warning: {filename.name} is not an animated image')
        self.has_default = self.frame_cnt > 1 and self.durations[0] == 0
        self.name = filename.stem
        # print(f'"{self.name}" frames={self.frame_cnt} fade={self.fade_frame}')
        return self

    def start(self) -> 'AnimatedImage':
        """Display the first frame of our sequence"""
        self.curr_frame = 1 if self.has_default else 0      # skip "default image"
        self.curr_loop = 0
        self.pic.update(data=self.frames[self.curr_frame])
        self.running = True
        self.fps_cnt = 0
        self.timer = self.fps_timer = millis()
        return self     # enables: var = AnimatedImage(...).start()

    def run(self):
        """Call this during Window event loop to cause animation to occur"""
        if self.running:
            now = millis()
            if (now - self.timer) < self.durations[self.curr_frame]:
                return      # display no cine before it's time
            self.curr_frame += 1
            if self.curr_frame >= self.frame_cnt:       # reached end of loop
                if self.loop:                           # finite loop count?
                    self.curr_loop += 1
                    if self.curr_loop >= self.loop:     # reached loop max?
                        self.stop()
                        return
                self.curr_frame = 1 if self.has_default else 0      # skip "default image"
            self.pic.update(data=self.frames[self.curr_frame])
            self.timer = now
            self.fps_cnt += 1

    def stop(self):
        """Stop animation and revert to original image"""
        if self.running:
            self.pic.update(data=self.save_image)
            self.running = False
            if self.stats:
                fps_time = millis() - self.fps_timer
                fps = self.fps_cnt / (fps_time / 1000)
                print(f'{self.name}: {self.fps_cnt} frames in {fps_time/1000:.3f} secs = {fps:.2f} fps')


if __name__ == '__main__':
    # For testing only:
    def test():
        sg.theme('Tan Blue')

        box_fn = Path('images/flicker.png')
        run_btn_fn = Path('images/btn_play_ani.png')
        pause_btn_fn = Path('images/btn_pause_ani.png')
        exit_btn_fn = Path('images/btn_power.png')
        img_bg_color = sg.theme_background_color()
        layout = [
            [sg.Image(filename=str(box_fn), key='-BOX-', background_color=img_bg_color)],
            [sg.Image(filename=str(run_btn_fn), key='-RUN-', background_color=img_bg_color, enable_events=True),
             sg.Image(filename=str(pause_btn_fn), key='-PAUSE-', background_color=img_bg_color, enable_events=True),
             sg.Push(),
             sg.Image(filename=str(exit_btn_fn), key='-EXIT-', background_color=img_bg_color, enable_events=True)]
        ]
        window = sg.Window('Testing AnimatedImage', layout=layout, finalize=True)
        ani_box = AnimatedImage(window['-BOX-'], box_fn, stats=True)
        run_btn = AnimatedImage(window['-RUN-'], run_btn_fn)
        pause_btn = AnimatedImage(window['-PAUSE-'], pause_btn_fn)

        while True:
            event, values = window.read(10)
            if event == sg.WINDOW_CLOSED or event == '-EXIT-' or event is None:
                break
            if event == '-RUN-':
                run_btn.start()
                ani_box.start()
                window.set_title(box_fn.stem)
            elif event == '-PAUSE-':
                pause_btn.start()
                ani_box.stop()
            elif event == sg.TIMEOUT_KEY:
                ani_box.run()
                run_btn.run()
                pause_btn.run()

            else:
                print(f'{event=} value={values.get(event)}')

        window.close()

    test()
