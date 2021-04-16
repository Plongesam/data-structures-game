import React, { Component } from "react";
import './LListGameboard.css';
import Stats from './LListStats';
import Cookies from 'universal-cookie';
import Queen from './antqueen.png';
import Ant from './ant.png';

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
    this.state = {
      // game settings
      difficulty:null,
      gameMode:null,
      players:null,
      board: null,
      gameID: null,
      token: "-1",
      username: "-1",
      ds: null,

      // in-game stats
      total_food: '',
      time: '',
      numChambers: '',
      total_ants: '',
      total_surface_ants: '',

      loading: true,
      spawningAnt: false,

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

    // add cookie variables to url
    let createGameURL = url + "game_board/llist_api/start_game/" + difficulty + "/" + players + "/" + ds
    let getGameURL = url + "game_board/llist_api/board/";

    /*
    //API call to start game
    let response = fetch(createGameURL);
    let game_id = await response.json();

    // save the get request response
    this.setState({ gameID: game_id['game_id']});
    cookies.set('game_id', game_id['game_id'], { path: '/'});

    //get request to api and include the dynamic game_id
    response = await fetch(getGameURL + game_id['game_id']);
    let game_board = await response.json();

    //set the state value from json response
    this.setState({ board: game_board });
    */


  }

  // api call to spawn an ant
  spawnAnt = async () => {
    this.setState({spawningAnt: true}) // delete this
    // get request to api
    let spawn_url = url + "game_board/llist_api/spawn_ant/" + this.state.gameID
    let response = await fetch(spawn_url);
    let board = await response.json();

    // set state variables 
    this.setState({board: board})
    this.setState({total_ants: board['total_ants']})
    this.setState({total_surface_ants: board['total_surface_ants']})
    this.setState({total_food: board['total_food_types']})

    this.setState({spawningAnt: true}) // keep this, state is set after api call 
    
  };

  handleGo = (event) => {
    alert('You have chosen to ' + this.state.action)
    event.preventDefault();
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value});
  }

  renderChoices= () => {
    return (
      <div className="choices">
        <form onSubmit={this.handleGo}>
          <p style={{margin:"0", padding:"0", color:'#5f5449', fontSize:"30px"}}>ANT ACTIONS MENU</p>
          <div style={{display:"flex", flexDirection:"row", justifyContent:"flex-start"}}>
            <select value={this.state.action} onChange={this.handleChange} name='action' >
              <option value="">Choose Action...</option>
              <option value="Dig chamber">Dig Chamber</option>
              <option value="Dig tunnel">Dig Tunnel</option>
              <option value="Forage">Forage</option>
              <option value="Move">Move</option>
              <option value="Fill in chamber">Fill Chamber</option>
            </select>
            
            <select value={this.state.action2} onChange={this.handleChange} name='action2'>
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
              <select value={this.state.chamber} onChange={this.handleChange} name='move_to_chamber'>
                <option value="chamber">Choose Chamber...</option> 
              </select>}

          <input type="submit" style={{background:'#36cf57', borderRadius:'5px'}} value="Go!"/>
          </div>
        </form>
      </div>
    )
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
        <rect style={{width:"160px", height:"130px", background:"white", opacity:".5", position:"absolute", top:"44%", left:"27%", border:"10px solid rgba(255, 255, 255, .5)", borderRadius:"5px"}}/>
        : null}
        {this.state.hovering? 
        <p style={{fontSize:"12px", color:"white", position:"absolute", top:"44%", left:"27.5%"}}>Click to spawn worker ant</p>
        : null}
        <span >
          <button ><img id="queenAnt" src={Queen} width ="130" style={{position:'absolute', top: '45.5%', left:'28%', padding:"5px 5px"}} 
          onMouseOver ={this.startHover} onMouseOut = {this.endHover}
          onClick={this.spawnAnt}/></button>
        </span>
        
        {this.state.spawningAnt ? 
        <figure id="egg" style={{background:"White", borderRadius:"50%", height:"50px", width:"30px", position:'absolute', top: '51%', left:'38%', transform:"rotate(300deg)"}} />
        : null
        }

      </div>
    );
  }
}

export default LListGameboard