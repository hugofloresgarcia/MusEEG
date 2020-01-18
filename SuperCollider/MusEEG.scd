/* SynthDefs that we're gonna use for each continuous and discrete command */
SynthDef(\sine, { arg freq;
	var sin, env;
	env = EnvGen.ar(Env.perc(releaseTime: 0.1), doneAction: 2);
	sin = SinOsc.ar(
		freq: Lag.kr([freq, freq], 1),
		mul: 0.1 * env);
	Out.ar(0, sin);
}).add;

SynthDef(\pulseTest, {
	arg ampHz=4,fund=40, maxPartial=4, width = 0.5;
	var amp1, amp2, freq1, freq2, sig1, sig2;
	amp1 = LFPulse.kr(ampHz, 0, 0.12) * 0.75;
	amp2 = LFPulse.kr(ampHz, 0.5, 0.12) * 0.75;
	freq1 = LFNoise0.kr(4).exprange(fund, fund*maxPartial).round(fund);
	freq2 = LFNoise0.kr(4).exprange(fund, fund*maxPartial).round(fund);
	freq1 = freq1 * LFPulse.kr(8, add:1);
	freq2 = freq2 * LFPulse.kr(6, add:1);
	sig1 = Pulse.ar(freq1, width, amp1);
	sig2 = Pulse.ar(freq2, width, amp2);
	sig1 = FreeVerb.ar(sig1, 0.7, 0.8, 0.25);
	sig2 = FreeVerb.ar(sig2, 0.7, 0.8, 0.25);
	Out.ar(0, sig1);
	Out.ar(1, sig2);
}).add;

SynthDef(\mouseThing, {
	var sin;
	sin = SinOsc.ar(
		mul: 1,
	    freq: 440);
	Out.ar(0, sin);
}).add;
Synth.new(\mouseThing);

~weirdPulseSynth = Synth.new(\pulseTest);≥
~weirdPulseSynth.set(\width, 0.25, \fund, 20);
~weirdPulseSynth.set(\maxPartial, 20);
~weirdPulseSynth.set(\ampHz, 1);

SynthDef(\playback, { arg buffer, startPos, envRelease = 1;
	var player, env;
	player = PlayBuf.ar(
		numChannels: 1,
		bufnum: buffer,
		rate: 1.0,
		startPos: startPos
	);
	env = EnvGen.ar(Env.perc(releaseTime: envRelease), doneAction: 2);
	Out.ar(0, env * player);
}).add;

/* Buffers for sound files */
~buffer = Buffer.read(s, "/Users/hugoffg/Documents/SuperCollider/DSG/gamelan_wav/BonangBarung/BonangBarungPl1.wav");
~glockBuffer = Buffer.read(s, "/Users/hugoffg/Documents/MusEEG/SuperCollider/glock.R.wav");


/* buses for setting control values */
~freqBus = Bus.control(s, 1);
~freqBus.setSynchronous(0);

~waitBus = Bus.control(s, 1);
~waitBus.setSynchronous(0.1);

~smileFunc = {
	arg val;
	val.postln;
	~freqBus.setSynchronous(val[1]);
	~waitBus.setSynchronous(val[2]);
};

/* OSCdefs for each different message we want */
OSCdef.new(\smileDef, ~smileFunc, '/smile').add;
OSCdef.new(\eyebrowsDef, ~smileFunc, '/eyebrows').add;
OSCdef.new(\lookleftDef, ~smileFunc, 'lookleft').add;
OSCdef.new(\lookrightDef, ~smileFunc, '/lookright').add;
OSCdef.new(\scrunchDef, ~smileFunc, '/scrunch').add;
OSCdef.new(\hardblinkDef, ~smileFunc, '/hardblink').add;

OSCFunc.trace;
Synth("sine", [\freq, 440]);


/*​ this is what python would send */
// 127.0.0.1 port 57120
m = NetAddr("localhost", 57120);
/* Routine({
 	inf.do({ arg i;
 		m.sendMsg("/smile", (60 + 12.rand).midicps, 0.1 + 0.2.rand);
 		0.3.wait;
 	});
 }).play;*/

~dsgSynth = Synth.new(\playback, [\buffer, ~buffer, \startPos, ~freqBus.asMap]);
~glockSynth = Synth.new(\playback, [\buffer, ~glockBuffer, \startPos, ~freqBus.asMap]);


 /* this is the supercollider routine */
Routine({
 	inf.do({
 		Synth(\playback, [\buffer, ~glockBuffer, \startPos, ~freqBus.asMap]);
 		(~waitBus.getSynchronous).wait;
	});
}).play;


Routine({
 	inf.do({ arg i;
 		m.sendMsg("/smile", ~glockBuffer.numFrames.rand, 0.01 + 0.5.rand);
 		0.3.wait;
	});
}).play;

/* this is the supercollider routine */
Routine({
	inf.do({
		~freqBus.getSynchronous.postln;
		Synth(\sine, [\freq, ~freqBus.getSynchronous]);
		0.3.wait;
	});
}).play;





