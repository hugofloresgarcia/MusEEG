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