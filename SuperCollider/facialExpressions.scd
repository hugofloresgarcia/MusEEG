(
//SynthDef for samples
SynthDef(\playback, { arg buffer, startPos = 0, envRelease = 1;
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

/* Buffers for samples */
~dsgBuffer = Buffer.read(s, "/Users/hugoffg/Documents/SuperCollider/DSG/gamelan_wav/BonangBarung/BonangBarungPl1.wav");
~glockBuffer = Buffer.read(s, "/Users/hugoffg/Documents/MusEEG/SuperCollider/glock.R.wav");
)
(

//localhost
m = NetAddr("localhost", 57120);

// buses where bandpower will be stored
~deltaBus = Bus.control(s, 1);
~thetaBus = Bus.control(s, 1);
~alphaBus = Bus.control(s, 1);
~betaBus  = Bus.control(s, 1);
~gammaBus = Bus.control(s, 1);

// functions that update bandpower buses
~setBase   = {arg val; ~baseline = val[1]; };
~deltaFunc = {arg val; ~deltaBus = val[1]; };
~thetaFunc = {arg val; ~thetaBus = val[1]; };
~alphaFunc = {arg val; ~alphaBus = val[1]; };
~betaFunc  = {arg val; ~betaBus  = val[1]; };
~gammaFunc = {arg val; ~gammaBus = val[1]; };

//function to just print what comes in
~justPrint = { arg val; val.postln; };

//bandpower bus array
~bandpowerBuses = [~deltaBus.value, ~thetaBus.value, ~alphaBus.value, ~betaBus.value, ~gammaBus.value];

/* OSCdefs for each different message we want */
OSCdef.new(\baseDef, ~setBase, '/baseline').add;
OSCdef.new(\deltaDef, ~deltaFunc, '/delta').add;
OSCdef.new(\thetaDef, ~thetaFunc, '/theta').add;
OSCdef.new(\alphaDef, ~alphaFunc, '/alpha').add;
OSCdef.new(\betaDef,  ~betaFunc,  '/beta' ).add;
OSCdef.new(\gammaDef, ~gammaFunc, '/gamma').add;

/* OSCdefs for each different message we want */
OSCdef.new(\smileDef, ~justPrint, '/smile').add;
OSCdef.new(\eyebrowsDef, ~justPrint, '/eyebrows').add;
OSCdef.new(\lookleftDef, ~justPrint, 'lookleft').add;
OSCdef.new(\lookrightDef, ~justPrint, '/lookright').add;
OSCdef.new(\scrunchDef, ~justPrint, '/scrunch').add;
OSCdef.new(\hardblinkDef, ~justPrint, '/hardblink').add;
)

OSCFunc.trace(true, true);
//soundmaking part

// Synths for samples
(
~dsgSynth = Synth.new(\playback, [\buffer, ~buffer, \startPos, ~startPos]);
~glockSynth = Synth.new(\playback, [\buffer, ~glockBuffer, \startPos, ~startPos]);
)
//playback routine
(
Routine({
 	inf.do({
 		Synth(\playback, [\buffer, ~glockBuffer, \startPos, ~startPos, \envRelease, ~envRelease]);
 		(~waitBus.getSynchronous).wait;
	});
}).play;
)
