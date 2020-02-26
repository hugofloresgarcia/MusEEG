////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   Patterns /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////
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

~attack = [0.01, 0.03];
~release = [0.1, 0.3];

(
~daisyRhythm = PatternProxy(Pseq(~mainRhythm*2, inf));
~daisyChord = PatternProxy(Pseq(~cloudChord + 33, inf));
~daisyHarmonic = PatternProxy(Pexprand(1, ~maxHarmonic, inf).round);
~daisyAtk = PatternProxy(Pwhite(0.1, 0.3, inf));
~daisyRel =  PatternProxy(Pwhite(0.1, 0.3, inf));
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

////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   Functions /////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////
(
// a smile changes the chord
~smileFunc = {
	arg val;
	val.postln;
	~daisyChord.source = Pseq((~chordPool.choose + ~keyCenters.choose), inf);
};

//scrunch increases the number of harmonics
~scrunchFunc = {
	arg val;
	val.postln;
	~maxHarmonic = ~maxHarmonic * 2;
	f(~maxHarmonic.round > 50){~maxHarmonic = 50};
	("max Harmonic " + ~maxHarmonic.asString).postln;
	~daisyHarmonic.source = Pexprand(1, ~maxHarmonic, inf).round;
};

//hardblink decreases the number of harmonics
~hardblinkFunc = {
	arg val;
	val.postln;
	~maxHarmonic = ~maxHarmonic / 2;
	if(~maxHarmonic.round == 0){~maxHarmonic = 1};
	("max Harmonic " + ~maxHarmonic.asString).postln;
	~daisyHarmonic.source = Pexprand(1, ~maxHarmonic, inf).round;
};

//lookleft decreases density
~lookleftFunc = {
	arg val;
	val.postln;
	~mainRhythm = ~mainRhythm * 1.5;
	~daisyRhythm.source = Pseq(~mainRhythm, inf);
};

//lookright increase density
~lookrightFunc = {
	arg val;
	val.postln;
	~mainRhythm = ~mainRhythm / 1.5;
	~daisyRhythm.source = Pseq(~mainRhythm, inf);
};
);

///////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   OSCdefs /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////

(
m = NetAddr("localhost", 57120);

// Band power parameters
OSCdef.new(\thetaDef, ~thetaFunc, '/theta').add;
OSCdef.new(\alphaDef, ~alphaFunc, '/alpha').add;
OSCdef.new(\betaDef , ~betaFunc, '/beta').add;
OSCdef.new(\gammaDef, ~gammaFunc, '/gamma').add;

// Facial Expressions
OSCdef.new(\neutralDef,   ~neutralFunc,  '/neutral').add;
OSCdef.new(\smileDef,     ~smileFunc,    '/smile').add;
OSCdef.new(\lookrightDef, ~lookrightFunc,'/lookright').add;
OSCdef.new(\lookleftDef,  ~lookleftFunc, '/lookleft').add;
OSCdef.new(\scrunchDef,   ~scrunchFunc,  '/scrunch').add;
OSCdef.new(\hardblinkDef, ~hardblinkFunc,'/hardblink').add;

OSCFunc.trace(true, true);
);