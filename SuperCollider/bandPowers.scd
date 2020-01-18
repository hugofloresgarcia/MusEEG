m = NetAddr("localhost", 57120);
~smileFunc = {
	arg val;
	val.postln;
};


~stressFunc = {
	arg val;
	~stressBus = val[1];
};

/* OSCdefs for each different message we want */
OSCdef.new(\deltaDef, ~smileFunc, '/delta').add;
OSCdef.new(\thetaDef, ~smileFunc, '/theta').add;
OSCdef.new(\alphaDef, ~smileFunc, '/alpha').add;
OSCdef.new(\betaDef, ~smileFunc, '/beta').add;
OSCdef.new(\gammaDef, ~smileFunc, '/gamma').add;

OSCFunc.trace(true, true);