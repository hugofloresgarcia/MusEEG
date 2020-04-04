function sleep(delay) {
    var start = new Date().getTime();
    while (new Date().getTime() < start + delay);
}

class QLearner {
  constructor(canvas_dim){
    this.learning_rate = 0.85;
    this.discount_factor = 0.9;
    this.randomness = 0.05;

    this.num_moves = 0;
    this.num_deaths = 0;
    this.cumulative_score = 0;

    this.current_score = 0;
    this.max_score = 0;

    this.q_table = {};
  }

  get_table_actions(state){
    if (this.q_table[state] == undefined){
      this.q_table[state] = {'up': 0, 'down':0, 'left':0, 'right': 0};
    }
    return this.q_table[state]
  }

  update_table(state_0, state_1, reward, action){
    let q0 = this.get_table_actions(state_0);
    let q1 = Object.values(this.get_table_actions(state_1));

    let new_entry = reward + this.discount_factor * Math.max(...q1) - q0[action];
    if (isNaN(new_entry)) {
      print(new_entry)
    }
    this.q_table[state_0][action] = q0[action] + this.learning_rate * new_entry;
  }

  get_best_action(state){
    let q = this.get_table_actions(state);
    let q_keys = Object.keys(q);
    let q_values = Object.values(q);

    let max_probability = Math.max(...q_values)
    let action;
    if (random(0, 1.0) < this.randomness){
      action = random(Object.keys(q));
    } else{
      if (max_probability == 0){ // if the max prob is zero, pick a random action
        action = random(Object.keys(q));
      } else {
        action = q_keys[q_values.indexOf(max_probability)];
      }
    }
    return action;
  }

  get_next_move(current_state){
    this.num_moves++;
    this.current_state = current_state;
    this.current_action = this.get_best_action(current_state);
    return this.current_action;
  }

  set_max_score(current_score){
    if (current_score > this.max_score) this.max_score = current_score;
  }

  show_scoreboard(x_pos, y_pos){
    //prints the scoreboard on the top corner
    this.log_table_button();
    // console.table(this.q_table);
    textSize(canvas_dim.y/25);
    let size =canvas_dim.y/25
    fill(125, 125, 250);
    let scores = {
      'MAX SCORE': this.max_score.toString(),
      'CURRENT SCORE': this.current_score.toString(),
      'CUMULATIVE SCORE': this.cumulative_score.toString(),
      'NUMBER OF DEATHS': this.num_deaths.toString(),
    }

    let keys = Object.keys(scores);
    let vals = Object.values(scores);

    for (let i = 0 ; i < keys.length ; i ++){
      text(keys[i] + ': ' + vals[i], x_pos, y_pos +  i * size);
    }
  }

  log_table(){
    console.table(this.q_table);
  }

  log_table_button(){
    if (this.log_button == undefined){
      this.log_button = p.createButton('print q table in console log')
      this.log_button.mousePressed(() => {this.log_table()})
      this.log_button.position(canvas_dim.x+50, canvas_dim.y/2+210);
    }
  }

  update(next_state, reward){
    this.update_table(this.current_state, next_state, reward, this.current_action)
    if (reward == - 1) {
      this.num_deaths++;
      this.set_max_score(this.current_score);
      this.current_score = 0;
    }
    if (reward == 1) {
      this.cumulative_score++;
      this.current_score++;
    }
  }

  load_checkpoint(){
    var input = document.createElement('input');
    input.type = 'file';
    var content = '';
    input.onchange = e => {
     var file = e.target.files[0];
           // setting up the reader
     var reader = new FileReader();
     reader.readAsText(file,'UTF-8');

     // here we tell the reader what to do when it's done reading...
     reader.onload = readerEvent => {
        content = JSON.parse(readerEvent.target.result); // this is the content!
        var f = (content) => {
          this.checkpoint =content;

          this.num_moves = content.num_moves;
          this.cumulative_score = content.cumulative_score;
          this.num_deaths = content.num_deaths;
          this.max_score = content.max_score;
          this.q_table = content.q_table;
        };
        f(content);
      }
    }
    input.click();
    // sleep(2200)


  }

  save_checkpoint(){
    let checkpoint = {
      "learning_rate": this.learning_rate,
      "radnomness": this.randomness,
      "discount_factor": this.discount_factor,
      "num_moves": this.num_moves,
      "num_deaths": this.num_deaths,
      "cumulative_score": this.cumulative_score,
      "max_score": this.max_score,
      "q_table": this.q_table
    };
    let checkpoint_str = JSON.stringify(checkpoint);
    download(checkpoint_str, 'checkpoint.json');
  }
}
