import React, { Component } from "react";
import './LListGameboard.css';
import Stats from './LListStats';
import Cookies from 'universal-cookie';
import Queen from './antqueen.png';
//import Ant from './ant.png';
import Ant from './AntComponent';
import ChamberComponent from './ChamberComponent.js';
import TunnelComponet from './TunnelComponet.js';


//this allows us to test separately locally and on Heroku by changing just one line
const local = "http://127.0.0.1:8000/";
const reactLocal = "http://localhost:3000/"
const remote = "https://data-structures-game.herokuapp.com/";

const url = local;

//export default function App() {
class LListGameboard extends Component {
  // constructor with default values
  constructor(props) {
    super(props);

    // for accessing variables between components
    this.llistRef = React.createRef();

    this.state = {
      // game settings
      difficulty:null,
      gameMode:null,
      player:null,
      board: null,
      gameID: null,
      token: "-1",
      username: "-1",
      ds: null,

      // in-game stats
      total_food: 0,
      food: [],
      time: 0,
      numChambers: 0,
      numTunnels: 0,
      chambers: null,
      total_ants: 0,
      total_surface_ants: 0,
      queen: false,

      loading: true,
      initial_load: true,
      spawningAnt: false, // 
      hatchingAnt: false, // false: no egg, true: egg

      // ant action values
      action: "",
      action2: "",
      action3: "",

    };
  }

  //component rendered at least once
  // fetch the data here
  async componentDidMount() {
    console.log("Component did mount");

    const cookies = new Cookies();

    // get variables used in url
    let difficulty = cookies.get('level');
    let players = cookies.get('playerList');
    let ds = cookies.get('gameDS');

    if (cookies.get('username') != null && cookies.get('token') != null) {
      if (cookies.get('username') != "" && cookies.get('token') != "") {
        this.setState({ username: cookies.get('username'), token: cookies.get('token') })
        players = players + "," + cookies.get('username');
      }
    }

    this.setState({player: cookies.get('playerList')})

    // add cookie variables to url
    let createGameURL = url + "llist_gameboard/llist_api/start_game/" + difficulty + "/" + players + "/" + ds;
    let getGameURL = url + "llist_gameboard/llist_api/board/";

    
    //API call to start game
    let response = await fetch(createGameURL);
    let game_id = await response.json(); 
    
    // save the get request response
    this.setState({ gameID: game_id['game_id']});
    cookies.set('game_id', game_id['game_id'], { path: '/'});

    //get request to api and include the dynamic game_id
    response = await fetch(getGameURL + game_id['game_id']);
    let game_board = await response.json(); 
    console.log(game_board);

    //set the state value from json response
    /*
    tunnels: game_board['tunnels'], 
    under_attack: game_board['under_attack'], 
    */
    this.setState({ board: game_board, 
                    numChambers: game_board['total_chambers'], 
                    numTunnels: game_board['total_tunnels'],
                    chambers: game_board['graph']['chambers'], 
                    total_ants: game_board['total_ants'], 
                    total_surface_ants: game_board['total_surface_ants'], 
                    food: game_board['total_food_types'],
                    total_food: game_board['total_food'],
                    queen: game_board['queen_at_head'],
                    time: game_board['curr_day'],
                  });

    
    // everything is loaded
    this.setState({loading: false, initial_load: false});
  }

  // api call to spawn an ant
  spawnAnt = async () => {
    if (this.state.spawningAnt == true ){
      alert('There is already an ant hatching, try again later.')
    }
    else {
      // get request to api
      let spawn_url = url+"llist_gameboard/llist_api/spawn_ant/" + this.state.board['game_id']
      this.setState({loading:true});

      // make the API call
      let spawn_response = await fetch(spawn_url);

      // spawn or dont spawn based on response status
      let game_board = await spawn_response.json();
      if( spawn_response.status >= 400) {
        //this.setState({error: })
        alert(game_board['invalid_action'])
      }
      else { // no erros, can spawn ant
        // set state variables
        this.setState({board: game_board})
        this.setState({ 
          total_ants: game_board['total_ants'], 
          //total_surface_ants: game_board['total_surface_ants'], 
          chambers: game_board['graph']['chambers'], 
          total_food: game_board['total_food'],
          time: game_board['curr_day'],
        });

        this.setState({spawningAnt: true}) // keep this, state is set after api call 
        this.setState({loading:false});
      
        // ant hatches after 5 seconds, egg dissappears, update the number of surface ants
        setTimeout(function() { //Start the timer
          this.setState({spawningAnt: false}) 
          this.setState({total_surface_ants: game_board['total_surface_ants']})
        }.bind(this), 5000)
      }
    }
  };

  handleGo = async (event) => {
    //alert('You have chosen to ' + this.state.action)
    event.preventDefault();
    var action1 = this.state.action;
    var action2 = this.state.action2;
    var action3 = this.state.action3;
    let action_url = "";
    
    // set action 2
    if( this.state.action2 == 0) { action2 = "surface";}
    else{ action2 = 'chamber' + this.state.action2;}
    
    if (this.state.action === 'Dig chamber') {
      action_url = url+"llist_gameboard/llist_api/dig_chamber/" + this.state.board['game_id'] + "/" + action2 + "/true" + "/None";
    }
    else if (this.state.action === 'Dig tunnel'){
      if( this.state.action3 == 0) { action3 = "surface";}
      else{ action3 = 'chamber' + this.state.action3;}
      action_url = url+"llist_gameboard/llist_api/dig_tunnel/" + this.state.board['game_id'] + '/' + action2 + '/None'; //+ action3
    }
    else if (this.state.action === 'Forage'){
      action_url = url+"llist_gameboard/llist_api/forage/" + this.state.board['game_id'] + "/" + this.state.board['difficulty'] + "/" + action2;
    }
    else if (this.state.action === 'Move'){ 
      if( this.state.action3 == 0) { action3 = "surface";}
      else{ action3 = "chamber" + this.state.action3;}
      action_url = url+"game_board/llist_api/move_ant/" + (this.state.board['game_id']).toString() + "/" + action2 + "/" + action3;
    }
    else if (this.state.action === 'Move food'){
      if( this.state.action3 == 0) { action3 = "surface";}
      else{ action3 = "chamber" + this.state.action3;}
      action_url = url+"llist_gameboard/llist_api/move_food/" + this.state.board['game_id'] + '/' + action2 + '/' + action3;
    }
    else if (this.state.action === 'Fill in chamber'){
      action_url = url+"llist_gameboard/llist_api/fill_chamber/" + this.state.board['game_id'] + '/' + action2;
    }

    alert('url: ' + action_url);

    // set url based on ant action chosen
    this.setState({loading:true});
    // make the API call
    let action_response = await fetch(action_url);

    // get the response 
    let game_board = await action_response.json();
    console.log(game_board);
    if( action_response.status >= 400) {
      alert(game_board['invalid_action'])
    }
    else { // no errors, fetch got a valid response
      // set state variables
      this.setState({board: game_board});
      this.setState({ 
        board: game_board, 
              numChambers: game_board['total_chambers'], 
              chambers: game_board['graph']['chambers'], 
              total_ants: game_board['total_ants'], 
              total_surface_ants: game_board['total_surface_ants'], 
              food: game_board['total_food_types'],
              total_food: game_board['total_food'],
              queen: game_board['queen_at_head'],
              time: game_board['curr_day'],
      });
    }
    this.setState({loading:false});
  };


  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value});
  }

  digChamber = async () => {
    this.setState({loading:true})

    this.setState({loading:false})
  }

  // renders the second select drop down options in ant actions:
  // the options change based on the first option choice
  dropDownOptions = () => {
    var optionList=[];
    var optionList2=[];
    var num2 = 0;
    //this.state.total_chambers
    if (this.state.action === 'Dig chamber') {
      var num = this.state.numTunnels
    }
    else if (this.state.action === 'Dig tunnel'){
      var num = this.state.numChambers
    }
    else if (this.state.action === 'Forage'){
      var num = this.state.numChambers
    }
    else if (this.state.action === 'Move' || this.state.action === 'Move food'){
      var num = this.state.numChambers
      num2 = this.state.numChambers
    }
    else if (this.state.action === 'Fill in chamber'){
      var num = this.state.numChambers
    }
    for(var i = 0; i <= num; i++) {
      optionList.push(i.toString());
    }
    for(var i = 0; i <= num2; i++) {
      optionList2.push(i.toString());
    }
    let dropDown = num > 0 && optionList.map((item, i) => {
      return ( <option value={i.toString()}>{i}</option> )
    }, this);
    let dropDown2 = num2 > 0 && optionList2.map((item, i) => {
      return ( <option value={i.toString()}>{i}</option> )
    }, this);

    return (
      <span>
        <select value={this.state.action2} onChange={this.handleChange} name='action2' style={{marginRight:"10px"}}>
          {dropDown}
        </select>
        {(this.state.action === 'Move' || this.state.action === 'Move food' || this.state.action === 'Dig tunnel' )&&
        <select value={this.state.action3} onChange={this.handleChange} name='action3' style={{marginRight:"10px"}}>
          {dropDown2}
        </select>}
      </span>
    );
  }

  renderChoices= () => {
    return (
      <div className="choices">
        <form onSubmit={this.handleGo}>
          <p style={{margin:"0", padding:"0", color:'#5f5449', fontSize:"30px"}}>ANT ACTIONS MENU</p>
          <div style={{display:"flex", flexDirection:"row", justifyContent:"flex-start"}}>
            <select value={this.state.action} onChange={this.handleChange} name='action' style={{marginRight:"10px"}} >
              <option value="">Choose Action...</option>
              <option value="Dig chamber">Dig Chamber</option>
              <option value="Dig tunnel">Dig Tunnel</option>
              <option value="Forage">Forage</option>
              <option value="Move">Move</option>
              <option value="Move food">Move Food</option>
              <option value="Fill in chamber">Fill Chamber</option>
            </select>
            
            {this.dropDownOptions()}
{/*
            {this.state.action === 'Move' &&
              <select value={this.state.chamber} onChange={this.handleChange} name='move_to_chamber' style={{marginRight:"10px"}}>
                <option value="chamber">Choose Chamber...</option> 
</select>}*/}

          <input type="submit" style={{background:'#36cf57', borderRadius:'5px'}} value="Go!"/>
          </div>
        </form>
      </div>
    )
  }

  // this is the react container that renders the chambers
  renderChambers = () => {
    
    const queen = this.state.queen_at_head
    // creates an array of Chamber Components
    var chamberArr=[];
    for(var prop in this.state.chambers){
      if(prop != 'surface') {
        chamberArr.push(<ChamberComponent ants={this.state.chambers[prop]['num_ants']} food={this.state.chambers[prop]['food']['total']} crumb={this.state.chambers[prop]['food']['crumb']} berry={this.state.chambers[prop]['food']['berry']} donut={this.state.chambers[prop]['food']['donut']} under_attack={this.state.chambers[prop]['under_attack']}/>);
      }
    }
    return chamberArr.map((singleChamber) => <li style={{listStyleType:"none"}}>{singleChamber}</li> );

  }

  renderTunnels = () => {
    const queen = this.state.queen_at_head
    var tunnelArr=[];

    for(var i = 1; i < this.state.numTunnels; i++) { // this.state.numTunnels 
      tunnelArr.push(<TunnelComponet/>);
    }

    return tunnelArr.map((singleTunnel) => <li style={{listStyleType:"none"}}>{singleTunnel}</li>);
  }

  renderSurfaceAnts = () => {
    const queen = this.state.queen_at_head
    // creates an array of Ant Components
    var ants=[];
    for(var i = 1; i < this.state.total_surface_ants; i++) {
      ants.push(<Ant/>);
    }

    return ants.map((ant) => <li style={{listStyleType:"none"}}>{ant}</li>);
  }

  // startHover and endHover are used when mouse is hovering over queen ant 
  startHover = () =>{
    this.setState({hovering: true})
  }
  endHover = () => {
    this.setState({hovering: false})
  }

  

  render() {
    return (
      <div className="gamepage">
        <div className="gradient-background"/>
        
        { this.renderChoices()}
        <div className="stats-container">
          <Stats time={this.state.time} food={this.state.total_food} ants={this.state.total_ants} chambers={this.state.numChambers}/>
        </div>

        {this.state.hovering? 
        <rect style={{width:"160px", height:"130px", background:"white", opacity:".5", position:"absolute", top:"44%", left:"34vh", border:"10px solid rgba(255, 255, 255, .5)", borderRadius:"5px"}}/>
        : null}
        {this.state.hovering? 
        <p style={{fontSize:"12px", color:"white", position:"absolute", top:"44%", left:"35vh"}}>Click to spawn worker ant</p>
        : null}
        <span >
          <button ><img id="queenAnt" src={Queen} width ="130" style={{position:'absolute', top: '45.5%', left:'35vh', padding:"5px 5px"}} 
          onMouseOver ={this.startHover} onMouseOut = {this.endHover}
          onClick={this.spawnAnt}/></button>
        </span>
        
        {this.state.spawningAnt ? 
        <figure id="egg" style={{background:"White", borderRadius:"50%", height:"50px", width:"30px", position:"absolute", top: "51%", left:"55vh", transform:"rotate(300deg)"}} />
        : null
        }
        <div className="surfaceAnts">
          {this.renderSurfaceAnts()}
        </div>
        <div className="chambers">
          {this.renderChambers()}
        </div>

        <div className="tunnels">
          {this.renderTunnels()}
        </div>


      </div>
    );
  }
}

export default LListGameboard