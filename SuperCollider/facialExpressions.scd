~smileFunc = {
	arg val;
	val.postln;
};

/* OSCdefs for each different message we want */
OSCdef.new(\smileDef, ~smileFunc, '/smile').add;
OSCdef.new(\eyebrowsDef, ~smileFunc, '/eyebrows').add;
OSCdef.new(\lookleftDef, ~smileFunc, 'lookleft').add;
OSCdef.new(\lookrightDef, ~smileFunc, '/lookright').add;
OSCdef.new(\scrunchDef, ~smileFunc, '/scrunch').add;
OSCdef.new(\hardblinkDef, ~smileFunc, '/hardblink').add;