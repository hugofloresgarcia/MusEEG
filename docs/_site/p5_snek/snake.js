// lets make a snake class. A snake needs to store a
// xy position vector
// xy direction vector
// drawing color
// number of rows and columns it has (num_steps)
// an array of positions that correspond to its body
class Snake {
  constructor (size, canvas_dim){// this is the function that gets called everytime I say new Player()
    this.size = size;
    this.canvas_dim = canvas_dim;
    this.num_steps = {
      x: floor(canvas_dim.x / this.size),
      y: floor(canvas_dim.y / this.size)
    };

    this.body = []; // an array that keeps track of the body
    this.body[0] = this.random_spawn(); // place the player in our starter position

    this.color = color(255, 255, 255);

    this.set_direction('right');
  }

  /// convenience method to get the head position of the snake
 get_head(){
   return this.body[this.body.length-1].copy();
 }

 // spawn a random snake head
  random_spawn(){
    let rand_x = round(random(this.num_steps.x)) * this.size;
    let rand_y = round(random(this.num_steps.y)) * this.size;
    return createVector(rand_x, rand_y);
  }

  // set the direction
  set_direction(dir){
    // // I just want to store the possible move actions here
    MOVE = {
        'none': createVector(0, 0),
        'up':  createVector(0, -this.size),
        'down': createVector(0, this.size),
        'left': createVector(-this.size, 0),
        'right': createVector(this.size, 0),
    }
    this.direction = MOVE[dir];
  }

  eat(food){
    if (this.get_head().equals(food.pos)){
      this.grow();
      return true;
    } else {
      return false;
    }
  }

  grow(){
    let new_head = this.get_head();
    new_head.add(this.direction);
    this.body.push(new_head);
  }

  // wrap around the screen if you reach one of the edges
  wrap(vector){
    if (vector.x < 0){
      vector.x = this.canvas_dim.x - this.size;
    }
    if (vector.x > (this.canvas_dim.x - this.size)){
      vector.x = 0;
    }
    if (vector.y < 0){
      vector.y = this.canvas_dim.y - this.size;
    }
    if (vector.y > (this.canvas_dim.y - this.size)){
      vector.y = 0;
    }
    return vector
  }

  collision_check(){
    if(this.body.length == 1){return false;}
    for (let i = 0; i < this.body.length-1; i++){
      let body_part = this.body[i];
      if(this.get_head().equals(body_part)){
        return true;
      }
    }
    return false;
  }

  // this is how the snake moves
  update(){
    let head = this.get_head(); // get the head
    head.add(this.direction); // add one to the head
    head = this.wrap(head)
    this.body.shift(); // remove the tail and shift the rest of the body down in the array
    this.body.push(head); // add the new head  to the array
  }

  draw(){
    noStroke();
    fill(this.color);
    for (let i = 0; i<this.body.length; i++){
      if(this.body[i].equals(this.get_head())){
        fill(color(230, 200, 200));
      }
      rect(this.body[i].x, this.body[i].y, this.size, this.size);
    }
  }

  die(){
    this.color = color(0, 0, 0);
    this.body = [];
  }
}


class Food {
  constructor(size, canvas_dim){
    this.pos = createVector(0, 0);
    this.eaten = false
    this.color = color(random(128, 255), random(128, 255), random(128, 255));
    this.size = size;
    // this is the a way to set up a grid so everything falls in place nicely
    this.num_steps = {
      x: floor(canvas_dim.x / this.size),
      y: floor(canvas_dim.y / this.size)
    };

    this.random_spawn();
  }

  random_spawn(){
    this.color = color(random(128, 255), random(128, 255), random(128, 255));
    let rand_x = round(random(this.num_steps.x-1)) * this.size;
    let rand_y = round(random(this.num_steps.y-1)) * this.size;
    this.pos = createVector(rand_x, rand_y);
  }

  draw(){
    noStroke();
    fill(this.color);
    rect(this.pos.x, this.pos.y, this.size, this.size);
  }

}
