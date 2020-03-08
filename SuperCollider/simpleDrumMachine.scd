
s.waitForBoot({

~tempo = 80;
TempoClock.default.tempo = ~tempo/60;

////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   hats /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////
(
SynthDef(
	name: \hats,
	ugenGraphFunc: {
		arg  freq = 100, amp = 0.6, rq = 1;
		var env, sig, filter, osc, noise;
		env = EnvGen.ar(
			envelope: Env.perc(
				attackTime: 0.00001,
				releaseTime: 0.05
			),
			doneAction: 2);

		noise = WhiteNoise.ar(0.5);
		osc = Decay.ar(
			in: SinOsc.ar(
				freq: freq*8,
				mul: 0.3
			),
			decayTime: 0.001);

		filter = RLPF.ar(
			in: noise,
			freq: 14e3,
			rq: rq);

		filter = HPF.ar(
			in: filter,
			freq: 4e3);

		sig = Mix.ar([  filter]) * env * amp;

		sig = FreeVerb.ar(
			in: sig,
			mix: 0,
			room: 1
		);


		Out.ar(0, sig!2);
}).add;
);

////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   kick /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////

(
SynthDef(
	name: \kick,
	ugenGraphFunc: {
		arg freq = 40, rq, amp = 0.5, atk = 0.001, rel = 0.4;
		var env, osc, filter, sig, mix;

		env = EnvGen.ar(
			envelope: Env.perc(
				attackTime: atk,
				releaseTime: rel,
			),
			doneAction: 2);


		osc = SinOsc.ar(freq + (freq * env * 0.05));

		filter = DynKlank.ar(
		specificationsArrayRef: `[
				Array.exprand(5, freq*6.asFloat, freq*3),     // frequencies
				Array.exprand(5, 0.0005, 0.001),     // amplitudes (default to 1.0)
				Array.rand(5, 0.0001, 0.001)        // ring times
		],
		input: PinkNoise.ar());

		mix = Mix.ar([osc, filter]);
				sig = (mix * env * amp).distort.softclip;

		Out.ar(0, sig!2);
}).add;
);

(
SynthDef(
	name: \kick2,
	ugenGraphFunc: {
		arg freq = 40, rq, amp = 0.5, atk = 0.001, rel = 0.1;
		var env, osc, filter, sig, mix;

		env = EnvGen.ar(
			envelope: Env.perc(
				attackTime: atk,
				releaseTime: rel,
			),
			doneAction: 2);


				osc = SinOsc.ar(freq + (env * (freq *  0.051)));

		filter = DynKlank.ar(
		specificationsArrayRef: `[
				Array.exprand(5, freq*15.asFloat, freq*9),     // frequencies
				Array.exprand(5, 0.005, 0.01),     // amplitudes (default to 1.0)
				Array.rand(5, 0.00025, 0.00025)        // ring times
		],
		input: PinkNoise.ar());

		mix = Mix.ar([osc, filter*2]);
				sig = (mix * env * amp).distort.distort.distort;

		Out.ar(0, sig!2);
}).add;
);


////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   snare /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////
(
SynthDef(
	name: \snare,
	ugenGraphFunc: {
		arg  freq = 150, amp = 0.6, rq = 1;
		var env, sig, filter, osc, noise;
		env = EnvGen.ar(
			envelope: Env.perc(
				attackTime: 0.00001,
				releaseTime: 0.05
			),
			doneAction: 2);

		noise = WhiteNoise.ar(0.6);
		osc = Decay.ar(
			in: LFTri.ar(
				freq: freq,
				mul: 0.1
			),
			decayTime: 0.001);

		sig = Mix.ar([ noise, osc]) * env * amp;

		filter = RLPF.ar(
			in: sig,
			freq: 20e3,
			rq: rq);

		sig = HPF.ar(
			in: sig,
			freq: 200);


		Out.ar(0, sig!2);
}).add;
);



////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   patterns /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////

(
~hihatRhythm = (0.25!14).addAll(0.125!4 );
Pdef(
	\hatpat,
	Pbind(
		\instrument, \hats,
		\dur, Pseq(~hihatRhythm, inf),
		\rq, 0.5,
));
);

(
~kickRhythm = [3, 3, 3, 1, 2, 4]* 0.25; //sixteenths
~kickRhythm2 = [3, 3, Rest(3), 1, 2, Rest(4)]* 0.25; //sixteenths

Pdef(
	\kickpat,
	Pbind(
		\instrument, \kick2,
		\dur, Pseq(~kickRhythm, inf),
		\midinote, Pseq([0, 0, 7, 0, 0, 7] + 48, inf) + Pwhite(-0.25, 0.25, inf),
		\amp, 0.7
));

Pdef(
	\kickpat2,
	Pbind(
		\instrument, \kick,
		\dur, Pseq(~kickRhythm2, inf),
		\note, Pseq([0, 0, 7, 0, 0, 7], inf),
		\octave, [2, 3],
		\amp, 0.7
));
);

(
~snareRhythm = 0.25!8;
~snareAmp = 0!8;
~snareAmp[4] = 0.6;

Pdef(
	\snarepat,
	Pbind(
		\instrument, \snare,
		\dur, Pseq(~snareRhythm, inf),
		\freq, 150,
		\amp, Pseq(~snareAmp, inf),
		\rq, 0.1
));
);

////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////// Functions ///////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////
(
~kickON = false;
~hatsON = false;
~snareON = false;

// a smile toggles the kick
~smileFunc = {
	arg val;
	val.postln;
	~kickON = ~kickON.not;
	if(~kickON,
		{ ~highKick = Pdef(\kickpat).play(quant: Quant.new(4, 0, -1))  },
		{~highKick.stop;})
};

//scrunch toggles the hats
~scrunchFunc = {
	arg val;
	val.postln;
	~hatsON = ~hatsON.not;
	if(~hatsON,{~hats = Pdef(\hatpat).play(quant: 1);},
		{~hats.stop;});
};

//hardblink toggles the snare
~hardblinkFunc = {
	arg val;
	val.postln;
	~snareON = ~snareON.not;
	if(~snareON,{~snare = Pdef(\snarepat).play(quant: 1);},
		{~snare.stop;});
};

//lookleft decreases tempo by 5 bpm
~lookleftFunc = {
	arg val;
	val.postln;
	~tempo = ~tempo + 5;
	TempoClock.default.tempo = ~tempo/60;
};

//lookright increases tempo  by 5 bpm
~lookrightFunc = {
	arg val;
	val.postln;
	~tempo = ~tempo - 5;
	TempoClock.default.tempo = ~tempo/60;
};
);

////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////// OSCdefs ///////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////

(
m = NetAddr("localhost", 57120);

// Band power parameters
OSCdef.new(\thetaDef, ~thetaFunc, '/theta').add;
OSCdef.new(\alphaDef, ~alphaFunc, '/alpha').add;
OSCdef.new(\betaDef, ~betaFunc, '/beta').add;
OSCdef.new(\gammaDef, ~gammaFunc, '/gamma').add;

// Facial Expressions
OSCdef.new(\neutralDef,   ~neutralFunc,  '/neutral').add;
OSCdef.new(\smileDef,     ~smileFunc,    '/smile').add;
OSCdef.new(\lookrightDef, ~lookrightFunc,'/lookright').add;
OSCdef.new(\lookleftDef,  ~lookleftFunc, '/lookleft').add;
OSCdef.new(\scrunchDef,   ~scrunchFunc,  '/scrunch').add;
OSCdef.new(\hardblinkDef, ~hardblinkFunc,'/hardblink').add;

);

////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////   Live /////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////
// Run this live for funs.
// facial expressions toggle rhythms in drum machine


})



