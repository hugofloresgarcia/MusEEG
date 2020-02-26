s.boot;

(
~infiniteHoldReverb =
{
	arg feedback = 0.3;
	var sig, local;

	sig = SoundIn.ar(0);
	local = LocalIn.ar(2) + sig.dup;

	5.do
	{
		local = AllpassN.ar(in: local, maxdelaytime: 1, delaytime: Rand(0.001, 0.1), decaytime: 0.5);
		local = PitchShift.ar(in: local, windowSize: 0.1, pitchRatio: MouseX.kr(0, 2));
	};


	LocalOut.ar(local*feedback);

	Out.ar(0, sig+local);

}.play;
)

~infiniteHoldReverb.set(\feedback,0.1)


(
// pitch shift input - USE HEADPHONES to prevent feedback.
play({
    PitchShift.ar(
        SoundIn.ar([0, 1]),    // stereo audio input
        0.1,             // grain size
        MouseX.kr(0,2),    // mouse x controls pitch shift ratio
        0,                 // pitch dispersion
        0.004            // time dispersion
    )
}))