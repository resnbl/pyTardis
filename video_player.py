"""
Video (actually, "animation") player to animate the TARDIS image(s) in the GUI.

There are 2 images animated separately: the beacon on top and the windows.
Each track may have its own combination of beacon and window animations.
"""
from pathlib import Path
from enum import Enum
import PySimpleGUI as sg
from animated_image import AnimatedImage


class BeaconSpeed(Enum):
    """Map beacon cycle speeds to the APNG files that implement them"""
    NORMAL = 'beacon'
    FAST = 'beacon_fast'
    SLOW = 'beacon_slow'


effects = {
    # Map effect names to TARDIS window and beacon animations
    'solidGreenEffect': ('box_green', BeaconSpeed.SLOW),
    'solidOrangeEffect': ('box_orange', BeaconSpeed.SLOW),
    'redGreenEffect': ('red_green', BeaconSpeed.NORMAL),
    'redBlueEffect': ('red_blue', BeaconSpeed.NORMAL),
    'riversEffect': ('box_pink', BeaconSpeed.SLOW),
    'flickerEfffect': ('flicker', BeaconSpeed.FAST),
    'heartBeatEffect': ('orange_beat', BeaconSpeed.NORMAL),
    'tardisTakeoff': ('blue_roll', BeaconSpeed.NORMAL),
    'beat8Effect': ('blue_fade_up', BeaconSpeed.FAST),
    'basicPalEffect': ('palette', BeaconSpeed.NORMAL)
}


class VideoPlayer:
    """Handle GUI Image animations"""
    def __init__(self, images_folder: Path):
        """Init with the location of our animations."""
        self._folder = images_folder
        self._beacon_ani: AnimatedImage | None = None
        self._box_ani: AnimatedImage | None = None

    def init(self, beacon: sg.Image, box: sg.Image):
        """Image initialization must be deferred until window widgets are defined"""
        self._beacon_ani = AnimatedImage(beacon)
        self._box_ani = AnimatedImage(box)

    def start(self, effect_name: str):
        """Load and display first image of animation."""
        box_file, beacon_speed = effects.get(effect_name, (None, None))

        if beacon_speed:
            file_path = self._folder / (beacon_speed.value + '.png')
            self._beacon_ani.load(file_path).start()

        if box_file:
            file_path = self._folder / (box_file + '.png')
            self._box_ani.load(file_path).start()

    def run(self):
        """Step our aminations along"""
        self._beacon_ani.run()
        self._box_ani.run()

    def stop(self):
        """Stop animating and restore original (static) image"""
        self._beacon_ani.stop()
        self._box_ani.stop()
