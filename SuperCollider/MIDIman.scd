/// reroute OSC messages as midi
(

~midiOut = MIDIOut.new(0);
MIDIIn.connectAll;
l = LinkClock.new(120/60);
m = NetAddr("localhost", 57120);

//default values
~dur = 0.25;
~arpeggioBool = true;
~scrambleBool = true;
~numRepeats = 6;
~numOctaves = 2;

OSCdef.new(\noteDur, {
	arg dur;
	dur.removeAt(0);
	~dur = dur.at(0).asFloat;
	~dur.postln;
},'/duration');

OSCdef.new(\arpeggioDef, {
	arg arpeggioBool;
	arpeggioBool.removeAt(0);
	~arpeggioBool = arpeggioBool.at(0).asBoolean;
}, '/arpeggiate') ;

OSCdef.new(\scrambleDef, {
	arg scrambleBool;
	scrambleBool.removeAt(0);
	~scrambleBool = scrambleBool.at(0).asBoolean;
	~scrambleBool.postln;
}, '/scramble');

OSCdef.new(\chordDef, {
	arg noteArray;
	noteArray.removeAt(0);
	// noteArray = noteArray ++ (noteArray+12);
	noteArray.postln;
	~playChord.value(noteArray);
}, '/chord');

OSCdef.new(\numRepeats, {
	arg numRepeats;
	numRepeats.removeAt(0);
	numRepeats.postln;
	~numRepeats = numRepeats.at(0).asInteger;
}, '/numRepeats');

~playChord = {
	arg noteArray;
	if(~scrambleBool, {noteArray = noteArray.scramble});

	~routine = Routine({
		// play all the notes
		if(~arpeggioBool,
			{
				~numRepeats.do({
					noteArray.do({
						arg note, count;
						~midiOut.noteOn(1, note, 69);
						~dur.wait;
						~midiOut.noteOff(1,  note, 0);
					});
			})},
			{
				noteArray.do({
					arg note, count;
					~midiOut.noteOn(1, note, 69);
				});
				(~dur * noteArray.size).wait;
				noteArray.do({
					arg note, count;
					~midiOut.noteOff(1, note, 0);
				});
			}
		);
	});

	l.play(task: ~routine, quant: 4);
};
);




// m.sendMsg("/chord", 60, 64, 67, 69, 71, 74);
