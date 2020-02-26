m = NetAddr("localhost", 57120);
~smileFunc = {
	arg val;
	val.postln;
};

~stressFunc = {
	arg val;
	~stressBus = val[1];
};

// Band power parameters
OSCdef.new(\thetaDef, ~thetaFunc, '/theta').add;
OSCdef.new(\alphaDef, ~alphaFunc, '/alpha').add;
OSCdef.new(\betaDef , ~betaFunc, '/beta').add;
OSCdef.new(\gammaDef, ~gammaFunc, '/gamma').add;

// Facial Expressions
OSCdef.new(\neutralDef, ~thetaFunc, '/neutral').add;
OSCdef.new(\smileDef, ~alphaFunc, '/smile').add;
OSCdef.new(\lookrightDef , ~betaFunc, '/lookright').add;
OSCdef.new(\lookleftDef, ~gammaFunc, '/lookleft').add;
OSCdef.new(\scrunchDef, ~gammaFunc, '/scrunch').add;

OSCFunc.trace(true, true);