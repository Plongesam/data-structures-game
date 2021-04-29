import React, { Component } from "react";
import './LListGameboard.css';
import Stats from './LListStats';
import Cookies from 'universal-cookie';
import Queen from './antqueen.png';
//import Ant from './ant.png';
import Ant from './AntComponent';
import ChamberComponent from './ChamberComponent.js';


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
      chambers:[],
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
      chamber: "",

    };
  }

  //component rendered at least once
  // fetch the data here
  async componentDidMount() {

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
    let createGameURL = url + "game_board/llist_api/start_game/" + difficulty + "/" + players + "/" + ds
    let getGameURL = url + "game_board/llist_api/board/";

    
    //API call to start game
    let response = await fetch(createGameURL);
    let game_id = await response.json(); 
    
    // save the get request response
    this.setState({ gameID: game_id['game_id']});
    cookies.set('game_id', game_id['game_id'], { path: '/'});

    //get request to api and include the dynamic game_id
    response = await fetch(getGameURL + game_id['game_id']);
    let game_board = await response.json(); 

    //set the state value from json response
    /*
    tunnels: game_board['tunnels'], 
    under_attack: game_board['under_attack'], 
    */
    this.setState({ board: game_board, 
                    numChambers: game_board['total_chambers'], 
                    chambers: game_board['ant_locations'], 
                    total_ants: game_board['total_ants'], 
                    total_surface_ants: game_board['total_surface_ants'], 
                    food: game_board['total_food_types'],
                    total_food: game_board['total_food'],
                    queen: game_board['queen_at_head'],
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
      //this.setState({spawningAnt: true})
      // get request to api
      let spawn_url = url+"game_board/llist_api/spawn_ant/" + this.state.board['game_id']
      this.setState({loading:true});

      // make the API call
      let spawn_response = await fetch(spawn_url);

      // spawn or dont spawn based on response status
      let game_board = await spawn_response.json();

      // set state variables
      this.setState({board: game_board})
      this.setState({ 
        total_ants: game_board['total_ants'], 
        //total_surface_ants: game_board['total_surface_ants'], 
        food: game_board['total_food_types'],
        total_food: game_board['total_food'],
      });

      this.setState({spawningAnt: true}) // keep this, state is set after api call 
      this.setState({loading:false});
      
      // ant hatches after 5 seconds, egg dissappears, update the number of surface ants
      setTimeout(function() { //Start the timer
        this.setState({spawningAnt: false}) //After 1 second, set render to true
      }.bind(this), 5000)
      //await sleep(5000);
      //this.setState({spawningAnt: false})
      this.setState({total_surface_ants: game_board['total_surface_ants']})
      

    } 
  };

  handleGo = async (event) => {
    //alert('You have chosen to ' + this.state.action)
    event.preventDefault();
    const action1 = this.state.action;
    const action2 = this.state.action2;
    const action3 = this.state.action3;
    let action_url = "";
    // set url based on ant action chosen
    this.setState({loading:true})
    
    switch (this.state.action){
      case 'Dig chamber': 
        action_url = url+"game_board/llist_api/dig_chamber/" + this.state.board['game_id'] + '/' + action2 + '/' //+ move_ant
        
      case 'Dig tunnel': 
        action_url = url+"game_board/llist_api/dig_tunnel/" + this.state.board['game_id'] + '/' + action2 + '/' //+ dest
        
      case 'Forage': 
        action_url = url+"game_board/llist_api/forage/" + this.state.board['game_id'] + '/' + this.state.difficulty + '/' //+ dest
        
      case 'Move': 
        action_url = url+"game_board/llist_api/";
        
      case 'Fill in chamber': 
        action_url = url+"game_board/llist_api/fill_chamber/" + this.state.board['game_id'] + '/' + action2
        
    }
    alert('You have chosen to ' + this.state.action)



  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value});
  }

  digChamber = async () => {
    this.setState({loading:true})

    this.setState({loading:false})
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
              <option value="Fill in chamber">Fill Chamber</option>
            </select>
            
            <select value={this.state.action2} onChange={this.handleChange} name='action2' style={{marginRight:"10px"}}>
              {this.state.action === 'Dig chamber' &&
                <option value="tunnel">Choose Tunnel...</option> }
              {this.state.action === 'Dig tunnel' &&
                <option value="chamber">Choose chamber...</option>
                }
              {this.state.action === 'Forage' &&
                <option value="ant">Choose ant...</option> }
              {this.state.action === 'Move' &&
                <option value="ant">Choose ant...</option> }
              {this.state.action === 'Fill in chamber' &&
                <option value="chamber">Choose chamber...</option> }
            </select>
            {this.state.action === 'Move' &&
              <select value={this.state.chamber} onChange={this.handleChange} name='move_to_chamber' style={{marginRight:"10px"}}>
                <option value="chamber">Choose Chamber...</option> 
              </select>}

          <input type="submit" style={{background:'#36cf57', borderRadius:'5px'}} value="Go!"/>
          </div>
        </form>
      </div>
    )
  }

  // this is the react container that renders the chambers
  // renders the first chamber as long as numChambers >= 1
  renderChambers = () => {
    
    const queen = this.state.queen_at_head
    // creates an array of Chamber Components
    var chamberArr=[];
    
    //for(var i = 1; i < 2; i++) {  //UNCOMMENT THIS LINE FOR TESTING, should be commenting when running the game normally
    for(var i = 1; i < this.state.total_surface_ants; i++) {  //COMMENT THIS LINE OUT FOR TESTING
      chamberArr.push(<ChamberComponent food={this.state.total_food}/>);
    }
  
    return chamberArr.map((singleChamber) => <li style={{listStyleType:"none"}}>{singleChamber}</li> );

  }

  renderSurfaceAnts = () => {
    const queen = this.state.queen_at_head
    // creates an array of Ant Components
    var ants=[];
    for(var i = 1; i < this.state.total_surface_ants; i++) {
      ants.push(<Ant/>);
    }

    //if (queen) {
    return ants.map((ant) => <li style={{listStyleType:"none"}}>{ant}</li>);
    //}
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
        <figure id="egg" style={{background:"White", borderRadius:"50%", height:"50px", width:"30px", position:'absolute', top: '51%', left:'38%', transform:"rotate(300deg)"}} />
        : null
        }
        <div className="surfaceAnts">
          {this.renderSurfaceAnts()}
        </div>
        <div className="chambers">
          {this.renderChambers()}
        </div>


      </div>
    );
  }
}

export default LListGameboard