"""Descriptors for each track played: audio and animation"""
from dataclasses import dataclass


@dataclass
class TrackInfo:
    """
    Track descriptor

    This structure associates a track "index" with an audio file and
    the animations to be displayed. Again, this is a hold-over from
    my Arduino code.
    """
    track: int = 0      # audio file prefix (-> "001_xxx.mp3", etc.)
    title: str = ''     # title (not filename)
    effect: str = ''    # animation descriptor

    def __str__(self) -> str:
        return f'{self.track:02d}: "{self.title}"'


TRACKS: list[TrackInfo] = [
    TrackInfo(17, "It's called the TARDIS", "beat8Effect"),
    TrackInfo(2, "Doctor Who theme excerpt", "heartBeatEffect"),
    TrackInfo(1, "TARDIS", "tardisTakeoff"),
    TrackInfo(9, "Hello, sweetie!", "riversEffect"),
    TrackInfo(3, "Don't blink", "beat8Effect"),
    TrackInfo(6, "Exterminate", "flickerEfffect"),
    TrackInfo(19, "Bigger on the inside", "riversEffect"),
    TrackInfo(5, "Strax suggests", "heartBeatEffect"),
    TrackInfo(4, "Clever", "redGreenEffect"),
    TrackInfo(10, "Wibbly Wobbly", "beat8Effect"),
    TrackInfo(8, "TARDIS door opens", "basicPalEffect"),
    TrackInfo(12, "Spoilers", "riversEffect"),
    TrackInfo(15, "You shouldn't have let me", "redBlueEffect"),
    TrackInfo(11, "Doctor Who theme (long)", "heartBeatEffect"),
    TrackInfo(14, "It goes ding", "basicPalEffect"),
    TrackInfo(16, "Codename the Doctor", "redBlueEffect"),
    TrackInfo(13, "Strax is runover", "heartBeatEffect"),
    TrackInfo(21, "Smaller on the outside", "riversEffect"),
    TrackInfo(7, "TARDIS Takeoff", "tardisTakeoff"),
    TrackInfo(18, "That does very very complicated", "redGreenEffect"),
    TrackInfo(20, "Cloister bell", "flickerEfffect")
]

CLOSE_EFFECT = TrackInfo(999, "You blinked!", "angelEffect")
