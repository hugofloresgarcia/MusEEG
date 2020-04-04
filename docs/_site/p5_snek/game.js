/*
this is where the main game logic takes place
it is controlling a Snake and Fruit object (from the snake.js file)
*/

class Game {

  constructor(block_size, canvas_dim){
    this.block_size = block_size;
    this.canvas_dim = canvas_dim;
    this.reset()

    this.player = 'human';

    // some typefaecing instructions
    this.font = loadFont('p5_snek/resources/8-Bit Madness.ttf');
    textSize(15);
    textFont(this.font);
    textAlign(CENTER, CENTER);


  }

  //get the game's state
  get_state(){
    // state prototype 1: fruit's position, and tail position relative to head
    // get food pos:
    let origin = this.snake.body[this.snake.body.length-1];

    let rel_food = new p5.Vector.sub(this.food.pos, origin);
    let rel_tail = new p5.Vector.sub(this.snake.body[0], origin);

    let food_state = rel_food.x.toString() + ',' + rel_food.y.toString();
    let tail_state = rel_tail.x.toString() + ',' + rel_tail.y.toString();

    let state = food_state + ';' + tail_state;

    return state
  }

  // reset the game
  game_reset(block_size, canvas_dim){
    this.snake = new Snake(block_size, canvas_dim); // snake from scratch
    this.food = new Food(block_size, canvas_dim); // food from scratch
    this.score = 0;
    this.is_game_over = false;
    this.show_main_menu = true;

    //buttons
    this.main_menu_buttons = false;
    this.game_over_buttons = false;
  }

  // this is just for aesthetic
  reset(){
    this.game_reset(this.block_size, this.canvas_dim);
  }

  soft_reset(){
    this.snake = new Snake(block_size, canvas_dim); // snake from scratch
    this.food = new Food(block_size, canvas_dim); // food from scratch
    this.score = 0;
  }

  main_menu_routine(){
    let text_size = this.canvas_dim.y/25;

    textSize(text_size);
    fill(255, 255, 255);

    text('SNEK', this.canvas_dim.x/2, this.canvas_dim.y/2);
    text('CHOOSE UR PLAYER', this.canvas_dim.x/2, this.canvas_dim.y/2 + text_size);

    textSize(text_size-2)
    text('(make a score of 10 for a surprise)', this.canvas_dim.x/2, this.canvas_dim.y/2+text_size*4);

    if (!this.main_menu_buttons){ // prevents from buttons being remade every loop
      this.main_menu_buttons = true;

      this.human_button = p.createButton('play w human');
      this.human_button.position(this.canvas_dim.x/2 - 40, this.canvas_dim.y/2 + text_size*2);

      this.human_button.mousePressed(() => {
          this.player = 'human';
          this.show_main_menu = false;
          this.human_button.position(-20, -20);
          this.ai_button.position(-20, -20);
        })

      this.ai_button = p.createButton('let ai play');
      this.ai_button.position(this.canvas_dim.x/2 - 40, this.canvas_dim.y/2 + text_size*3);

      this.ai_button.mousePressed(() =>{
          this.player = 'q_learner';
          this.q_learner = new QLearner();
          this.show_main_menu = false;
          this.human_button.position(-20, -20);
          this.ai_button.position(-20, -20);
        });
    }
  }

  game_loop(){
    let reward = 0
    if (this.player == 'q_learner'){
      let action = this.q_learner.get_next_move(this.get_state());
      this.snake.set_direction(action);
    }
    this.snake.update(); // update (move) the snake depending on keyboard position

    reward = 0; //default value, gets overwritten if collission or eating

    if (this.snake.collision_check()){ // check for a snake body collision
      reward = -1;
      if (this.player == 'human') {this.is_game_over = true; }// if true, set game to over
      if (this.player == 'q_learner'){this.soft_reset();}
    }

    if (this.snake.eat(this.food)){ // check to see if the snake ate the food
      reward = 1;
      this.score++; //if it did, raise the score
      this.food.random_spawn(); // spawn a new fruit
    }

    if (this.player == 'q_learner'){
      this.q_learner.update(this.get_state(), reward);
    }
  }

  game_over_routine(){
    //IF THE GAME IS OVER, DO THIS INSTEAD
    background(0, 0, 255);

    let text_size = this.canvas_dim.y/20;
    textSize(text_size);
    fill(255, 255, 255);

    text('GAME OVER \n U SUCK', this.canvas_dim.x/2, this.canvas_dim.y/2);
    this.show_scoreboard(this.canvas_dim.x/2, this.canvas_dim.y/2 + text_size*2);
    this.snake.die();

    if (!this.game_over_buttons){
        this.reset_button= p.createButton('RESET');
        this.reset_button.mousePressed(() => {this.reset(); this.reset_button.position(-20,-20)});
        this.reset_button.position(this.canvas_dim.x/2-40, this.canvas_dim.y/2 + text_size*4);
        this.game_over_buttons = true;

    }
  }

  // THIS IS THE IMPORTANT code
  // it runs in a loop in the draw() function of the sketch.js file
  update(){
    if (this.show_main_menu){ // first, go to the main menu
      this.main_menu_routine();
    } else { // if you're out of the main menu

      if (!this.is_game_over){ //first, check to see if the game is over
        this.game_loop(); // if the game isn't over, keep the game loop going
      }
      else{ // if the game is over, show game over menu
        this.game_over_routine();
      }
    }
  }


  draw(){
    if (this.show_main_menu){ // first, go to the main menu
    } else { // if you're out of the main menu

      if (!this.is_game_over){ //first, check to see if the game is over
        //drawing
        this.snake.draw();
        this.food.draw();
        // show the score_board
        this.show_scoreboard(40, 40);
      }
      else{ // if the game is over, show game over menu
      }
    }
  }


  set_keyboard_control(keyCode){
    //SET THE DIRECTION OF THE SNAKE DEPENDING ON THE KEYCODE
    if (this.player == 'human'){
      if (keyCode == LEFT_ARROW){
        this.snake.set_direction('left');
      } else if (keyCode == RIGHT_ARROW){
        this.snake.set_direction('right');
      } else if (keyCode == UP_ARROW){
        this.snake.set_direction('up');
      } else if (keyCode == DOWN_ARROW){
        this.snake.set_direction('down');
      }
    }
    return false
  }

  show_scoreboard(x_pos, y_pos){
    //prints the scoreboard on the top corner
    textSize(this.canvas_dim.y/25);
    fill(255, 255, 255);
    text("SCORE\n" + this.score.toString(), x_pos, y_pos);
  }
}
