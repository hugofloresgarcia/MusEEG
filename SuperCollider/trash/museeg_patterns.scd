(~mainRhythm = [0.1, 0.2, 0.3, 0.2, 0.1];

//some chords to choose from

~cloudChord = [0, 2, 7, 14, 16, 21];

~openChord69 = [0, 4, 9, 14, 18];
~closedChord69 = [0, 12, 14, 16, 21];
~openChordmaj7 = [0, 7, 11, 16, 19];
~closedmaj7 = [0, 2, 4, 7, 11];

~chordPool = [~cloudChord, ~openChord69, ~closedChord69, ~openChordmaj7, ~closedmaj7];
~keyCenters = [36, 41];

~maxHarmonic = 3;

(
~daisyRhythm = PatternProxy(Pseq(~mainRhythm*2, inf));
~daisyChord = PatternProxy(Pseq(~cloudChord + 33, inf));
~daisyHarmonic = PatternProxy(Pexprand(1, ~maxHarmonic, inf).round);
~daisyAtk = PatternProxy(Pwhite(0.1, 0.3, inf));
~daisyRel =  PatternProxy(Pwhite(1, 3, inf));
~daisyAmp = PatternProxy(Pkey(\harmonic).reciprocal * 0.3);

~daisyIndex = PatternProxy(Pwhite(0, 0, inf));
~daisyRatio = PatternProxy(Pexprand(1, 1, inf).round);

(~daisypat = Pbind(
	\instrument, \fmsynth,
	//try different permutations of this
	\dur, ~daisyRhythm,
	\midinote,~daisyChord,
	\harmonic, ~daisyHarmonic,
	\atk, ~daisyAtk,
	\rel, ~daisyRel,
	\amp, ~daisyAmp,
	\pan, Pwhite(-0.8, 0.8, inf),

	\index, ~daisyIndex,
	\ratio, ~daisyRatio,

	\bla, Pfunc {
		arg in;
		if(in[\ratio].round - in[\ratio] != 0,{
			m.sendMsg("/lily", in[\harmonic], in[\amp], in[\pan], in[\index], in[\ratio]);
		},
		{
			m.sendMsg("/daisy", in[\harmonic], in[\amp], in[\pan], in[\index], in[\ratio]);
		});
	},
);
);
);
);