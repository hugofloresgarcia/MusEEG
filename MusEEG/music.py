import mido
import time
from audiolazy.lazy_midi import str2midi
from MusEEG import parentDir, port, closePort, resetPort


class music:
    midiChannel=0
    tempo = 120

    def panic(self):
        port.panic()
        resetPort()

    def pause(self,nQuarterNotes):
        time.sleep((nQuarterNotes)*1/self.tempo*60)

class chord(music):
    def __init__(self, notelist):
        self.notelist = notelist

    def play(self, vel=64):
        for notes in self.notelist:
            msg = mido.Message('note_on', note=str2midi(notes), velocity=vel, channel=self.midiChannel)
            port.send(msg)

    def stop(self):
        for notes in self.notelist:
            msg = mido.Message('note_off', note=str2midi(notes), channel=self.midiChannel)
            port.send(msg)

    def arpeggiate(self, notelength, vel, numTimes):
        for i in range(numTimes):
            for notes in self.notelist:
                msg = mido.Message('note_on', note=str2midi(notes), velocity=vel, channel=self.midiChannel)
                port.send(msg)
                self.pause(notelength)

class melody(music):
    currentTime = 0

    def __init__(self, midiname):
        self.midi = mido.MidiFile(midiname)
        self.track = mido.MidiTrack
        self.midi.tracks.append(self.track)

    def addnote(self, note, duration, vel=64):
        msgon = mido.Message('note_on', note=str2midi(note), velocity=vel, channel=self.midiChannel, time=self.currentTime)
        port.send(msgon)
        self.pause(mido.second2tick(duration/60*self.tempo))
        msgoff = mido.Message('note_off', note=str2midi(note), velocity=vel, channel=self.midiChannel, time=self.currentTime+duration)
        port.send(msgoff)


#todo: add melody class