// Coding Rainbow
// Daniel Shiffman
// http://patreon.com/codingtrain
// Code for: https://youtu.be/E1B4UoSQMFw

// variables: A B
// axiom: A
// rules: (A → AB), (B → A)
var angle;
var axiom = "X";
var sentence = axiom;
var len = 1300;

var rules = [];
rules[0] = {
  a: "F",
  b: "FF"
}

rules[1] = {
  a: "X",
  b: "F[+X]F[-X]+X"
}

function generate() {
  len *= 0.5;
  var nextSentence = "";
  for (var i = 0; i < sentence.length; i++) {
    var current = sentence.charAt(i);
    var found = false;
    for (var j = 0; j < rules.length; j++) {
      if (current == rules[j].a) {
        found = true;
        nextSentence += rules[j].b;
        break;
      }
    }
    if (!found) {
      nextSentence += current;
    }
  }
  sentence = nextSentence;
  createP(sentence);
  turtle();

}


let w = 10;
function turtle() {
  let idx = round(random(0, palettes.length));

  let c = palettes[idx];

  w  = w -1;

  background(51);
  resetMatrix();
  translate(width / 2, height);
  strokeWeight(6);
  stroke(color(255-94, 255-92, 255-84));
  for (var i = 0; i < sentence.length; i++) {
    var current = sentence.charAt(i);

    if (current == "F") {
      line(0, 0, 0, -len);
      translate(0, -len + random(-len/10, len/10));
    } else if (current == "+") {
      rotate(angle);
    } else if (current == "-") {
      rotate(-angle)
    } else if (current == "[") {
      push();
    } else if (current == "]") {
      pop();
    }
  }
}

var palettes = [];

function setup() {
    createCanvas(3000, 3000);
  background(color(200, 200, 200));
  palettes = [color(72, 191, 132), color(72, 191, 132), color(255, 186, 215),
              color(122, 132, 80), color(122, 132, 80), color(203, 243, 210),
              color(76, 46, 5)   , color(76, 46, 5), color(183, 192, 238),
              color("#99A58D"), color("#99A58D"), color("#5A2D3C"),
              color("#5F6117"), color("#5F6117"), color("#FBED6B"),
              color("#5F6117"), color("#5F6117"), color("#FA7557"),
              color("#5F6117"), color("#5F6117"), color("#E67251"),
              color("#8F7579"), color("#8F7579"), color("#60522A"),
              color("#DFC692"), color("#DFC692"), color("#F1877E"),
              color("#3F556E"), color("#3F556E"), color("#F1877E"),
              color("#3F556E"), color("#3F556E"), color("#59484F"),
              color("#3F556E"), color("#3F556E"), color("#CC5543"),
              color("#3F556E"), color("#3F556E"), color("#DBE6AF"),
              color("#3F556E"), color("#3F556E"), color("#CC5543"),
              color("#3F556E"), color("#3F556E"), color("#455C4F"),
            ];




  angle = radians(25);

  createP(axiom);
  turtle();
  var button = createButton("generate");
  button.mousePressed(generate);
}
