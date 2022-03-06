"""
This class controls the Tardis audio and animations.
"""
import PySimpleGUI as sg
from tracks import TRACKS
from audio_player import AudioPlayer
from video_player import VideoPlayer

IDLE_TITLE = '..idle..'
MAX_VOL = AudioPlayer.MAX_VOL
INIT_VOL = AudioPlayer.INIT_VOL


class TardisController:
    """TARDIS audio/visual controller"""
    def __init__(self):
        self._trk_idx = 0
        self._audio = AudioPlayer()
        self._video = VideoPlayer()
        self.duration = 0

    def set_images(self, beacon: sg.Image, box: sg.Image):
        """Do animation initialization after window widgets are defined"""
        self._video.init(beacon, box)

    @property
    def titles(self) -> list[str]:
        return [ti.title for ti in TRACKS]

    @property
    def track_index(self) -> int:
        return self._trk_idx

    @property
    def is_playing(self) -> bool:
        return self._audio.is_playing

    @property
    def progress(self) -> int:
        return round(100 * self._audio.current_time / self.duration) if self.is_playing else 0

    def play(self) -> str:
        ti = TRACKS[self._trk_idx]
        self.duration = self._audio.play(ti.track)
        if self.duration:
            self._video.start(ti.effect)
            dur_secs = self.duration / 1000
            return f'{TRACKS[self._trk_idx].title}: {dur_secs:.1f}'
        else:
            return IDLE_TITLE

    def select_title(self, title: str):
        for idx, ti in enumerate(TRACKS):
            if title == ti.title:
                self.stop()
                self._trk_idx = idx
                break
        else:
            print(f'Title "{title}" not found')

    def select_prev(self):
        self.stop()
        self._trk_idx = (self._trk_idx - 1) % len(TRACKS)

    def select_next(self):
        self.stop()
        self._trk_idx = (self._trk_idx + 1) % len(TRACKS)

    def stop(self):
        self._audio.stop()
        self._video.stop()

    def set_volume(self, vol: int):
        self._audio.set_volume(vol)

    def run_effects(self):
        self._video.run()
