"""
Rudimentary audio player implemented with VLC MediaPlayer.

VLC was chosen because it affords the most control with async playback and accepts
numerous audio formats (not just .WAV). It does, of course, require that the excellent
VLC Player application be installed on your machine.

(Actually, using the PyObjC/NSSound player on Mac OS is even better, but is not cross-platform...)

This class expects audio files to be laid out as:
    ./audio/
        001_filename.ext

        002_filename.ext

This naming convention is based on earlier work not really necessary here.
"""
from pathlib import Path
from time import sleep
from vlc import MediaPlayer, State      # State is a pseudo-Enum which can't be type checked(?)
from timed_print import elapsed_print as eprint


class AudioPlayer:
    """Simple VLC wrapper"""
    INIT_VOL = 8
    MAX_VOL = 11        # see "This is Spinal Tap"

    def __init__(self, audio_folder: Path):
        self._volume = AudioPlayer.INIT_VOL
        self._vlc: MediaPlayer | None = None        # new player for each track
        self._folder = audio_folder

        if not self._folder.is_dir():
            raise FileNotFoundError(f'AUDIO folder not found: {self._folder}')

    @property
    def is_playing(self) -> bool:
        """Is our player actually playing?"""
        return self._vlc and self._vlc.is_playing()

    @property
    def duration(self) -> int:
        """Duration of current track in msecs"""
        return max(self._vlc.get_length(), 0) if self._vlc else 0

    @property
    def current_time(self) -> int:
        """How long current track has played in msecs"""
        return max(self._vlc.get_time(), 0) if self._vlc else 0

    def set_volume(self, vol: int):
        """Set player volume, scaling from our limits to VLC's."""
        # cache volume setting in case not currently playing
        self._volume = 0 if vol < 0 else AudioPlayer.MAX_VOL if vol > AudioPlayer.MAX_VOL else vol
        if self._vlc:
            vlc_vol = round(100 * self._volume / AudioPlayer.MAX_VOL)
            self._vlc.audio_set_volume(vlc_vol)

    def play(self, track_num: int) -> int:
        """Play clip from specified folder and track numbers"""
        self.stop()
        file_glob = f'{track_num:03d}*.*'
        file = next(self._folder.glob(file_glob), None)       # use 1st (only?) matching file
        if not file:
            eprint(f'Audio track not found: {self._folder}/{file_glob}')
            return 0

        # Create a new player for each audio track
        self._vlc = MediaPlayer(file)
        vlc_vol = round(100 * self._volume / AudioPlayer.MAX_VOL)
        self._vlc.audio_set_volume(vlc_vol)
        self._vlc.play()
        while self._vlc.get_state().value < State.Playing.value:      # noqa
            sleep(.002)             # give player a chance to load file & start playing
        return self.duration        # (not available until actually playing)

    def stop(self):
        """Silence..."""
        if self._vlc and self._vlc.is_playing():
            self._vlc.stop()
            while self._vlc.get_state() == State.Playing:      # noqa
                sleep(.002)      # give player a chance to clean up
