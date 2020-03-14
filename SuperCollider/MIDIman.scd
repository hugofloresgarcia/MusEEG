/// reroute OSC messages as midi
(
MIDIIn.connectAll;
~clock = TempoClock.new(120/60);
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
	~numRepeats = numRepeats.at(0);
}, '/chord');

~playChord = {
	arg noteArray;
	if(~scrambleBool, {noteArray = noteArray.scramble});

	~routine = Routine({
		// play all the notes
		if(~arpeggioBool,
			{
				4.do({
					noteArray.do({
						arg note, count;
						MIDIIn.doNoteOnAction(1, 1, note, 69);
						~dur.wait;
						MIDIIn.doNoteOffAction(1, 1, note, 0);
					});
			})},
			{
				noteArray.do({
					arg note, count;
					MIDIIn.doNoteOnAction(1, 1, note, 69);
				});
				(~dur * noteArray.size).wait;
				noteArray.do({
					arg note, count;
					MIDIIn.doNoteOffAction(1, 1, note, 0);
				});
			}
		);
	});

	~clock.play(task: ~routine, quant: 4);
};
);


OSCFunc.trace(false,true);



m.sendMsg("/chord", 60, 64, 67, 69, 71, 74);
