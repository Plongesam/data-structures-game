import React from 'react';
import {TextField} from '@material-ui/core';
import Cookies from 'universal-cookie';
import {Link} from "react-router-dom";

//set the construct by sharing/setting the constructor states between
// Home and GameInfo & bind the state value's to the input change that happens
class GameInfo extends React.Component {
    constructor(props) {
        super(props);
        this.customNodeRef = React.createRef();
        //hard coded defaults
        this.state = {level:'Easy', playerList:'Enter player(s) name', gameDS:'AVL'};
        //set cookies in constructor so that initial values work when game play settings are not customized
        const cookies = new Cookies();
        cookies.set('level', this.state.level, { path: '/' });
        cookies.set('playerList', this.state.playerList, { path: '/' });
        cookies.set('gameDS', this.state.gameDS, { path: '/' });
        this.handleInput = this.handleInput.bind(this);
        this.submitDSG = this.handleInput.bind(this)
        
    }
    /*
    changeLink() {
        //Gets currently sellected DS game and the start button and save to variables
        var ds = document.getElementById('gameDS').value;
        var startGame = document.getElementById('start_game');
        //If AVL is selected, change link to go to /game_board
        if (ds == "AVL")
        {
            startGame.innerHTML = "<Link className=\"flex justify-center shadow-x1 transition duration-500 ease-in-out bg-blue-500 hover:bg-red-500 transform hover:-translate-y-1 hover:scale-105 bg-blue-300 border-blue-350 border-opacity-50 rounded-lg shadow-x1 p-5 rounded text-x1 font-bold\" to=\"/game_board\" name=\"start_game\"> Start Game </Link>"
        }
        //If Either linked list is selected, change link to /llgame_board (right now it is set to /game_board/llist_api)
        //That is where the gamepage is located in /gameboard but we realized we need our own linked list gameboard. Once 
        // our game_board is made, will link the start button to the correct gameboard for the correct game 
        else {
            startGame.innerHTML = "<Link className=\"flex justify-center shadow-x1 transition duration-500 ease-in-out bg-blue-500 hover:bg-red-500 transform hover:-translate-y-1 hover:scale-105 bg-blue-300 border-blue-350 border-opacity-50 rounded-lg shadow-x1 p-5 rounded text-x1 font-bold\" to=\"/game_board/llist_api\" name=\"start_game\"> Start Game </Link>"

        }
    }
*/
    changeLink = (event) => {
        this.setState({ [event.target.name]: event.target.value});
    }

    
    
    //this handls the change in input and is later binded to state values
    //cookies then are set to the changed values
    handleInput = async (e) => {
    await this.setState({ [e.target.name]: e.target.value });
        

    //update cookie values when game is customized
    const cookies = new Cookies();
    cookies.set('level', this.state.level, { path: '/' });
    cookies.set('playerList', this.state.playerList, { path: '/' });
    cookies.set('gameDS', this.state.gameDS, { path: '/' });
       
    }


render(){

    return(
        //grid stores the different options that are set in the modal form
        // each value input changes handleInput and is rebinded to the state value
        //that is changed and resets the cookies

        <div className="w-full md:max-w-md mt-6">
            <span>
            <div className="card bg-gray-200 shadow-2xl rounded-2xl px-4 py-4 mb-4 ">

            <div className="space-y-10 flex justify-center">
              <h1 className="space-y-20 text-3xl text-center font-semibold text-gray-800 mb-2">Play Now</h1>
            </div>

        <form onSubmit={this.handleSubmit}  >

            <div className="form-group" className="space-y-2">
            <label className="text-xl text-center font-semibold text-gray-800 mb-2"
                   htmlFor='game'>Data Structure:</label>
                <svg className="w-2 h-2 absolute top-0 right-0 m-4 pointer-events-none"
                     xmlns="http://www.w3.org/2000/svg" viewBox="0 0 412 232"><path
                    d="M206 171.144L42.678 7.822c-9.763-9.763-25.592-9.763-35.355 0-9.763 9.764-9.763 25.592 0 35.355l181 181c4.88 4.882 11.279 7.323 17.677 7.323s12.796-2.441 17.678-7.322l181-181c9.763-9.764 9.763-25.592 0-35.355-9.763-9.763-25.592-9.763-35.355 0L206 171.144z"
                    fill="#648299" fill-rule="nonzero"/></svg>
                    <select  className="space-x-60 border border-gray-300 rounded-lg text-gray-600 h-10 pl-5 pr-10 bg-white hover:border-gray-400 focus:outline-none appearance-none" type='text' id="game" value={this.state.gameDS} onInput={this.handleInput} name='gameDS'
                            label='DSgame' style={{marginBottom: '1em'}} onChange={this.changeLink}>
                        <option value="AVL">AVL</option>
                        <option value="LLIST-standard">Linked List Standard</option>
                        <option value="LLIST-survival">Linked List Survival</option>


                     </select>
            </div>

            <div class="form-group" className="space-y-2">

            <label  className="text-xl text-center font-semibold text-gray-800 mb-2" for='difficulty-level'>Difficulty:</label>
                <svg className="w-2 h-2 absolute top-0 right-0 m-4 pointer-events-none"
                     xmlns="http://www.w3.org/2000/svg" viewBox="0 0 412 232"><path
                    d="M206 171.144L42.678 7.822c-9.763-9.763-25.592-9.763-35.355 0-9.763 9.764-9.763 25.592 0 35.355l181 181c4.88 4.882 11.279 7.323 17.677 7.323s12.796-2.441 17.678-7.322l181-181c9.763-9.764 9.763-25.592 0-35.355-9.763-9.763-25.592-9.763-35.355 0L206 171.144z"
                    fill="#648299" fill-rule="nonzero"/></svg>
                    <select className="space-x-60 border border-gray-300 rounded-lg text-gray-600 h-10 pl-5 pr-10 bg-white hover:border-gray-400 focus:outline-none appearance-none" type='text' id='difficulty-level' value={this.state.level} name='level' onChange={this.handleInput} label='Difficulty Level' style={{ marginBottom: '1em' }}  >
                        <option value="Easy">Easy</option>
                        <option value="Medium">Medium</option>
                        <option value="Hard">Hard</option>
                     </select>
            </div>

                    <TextField
                        required
                        fullWidth
                        name='playerList'
                        label='players'
                        value={this.state.playerList}
                        onChange={this.handleInput}
                        style={{ marginBottom: '1em' }}
                    />

                <div className="space-y-10"><br></br></div>

                    <ul>
                    <li>
                        {this.state.gameDS === 'AVL' && 
                            <Link className="flex justify-center shadow-xl transition duration-500 ease-in-out bg-blue-500 hover:bg-red-500 transform hover:-translate-y-1 hover:scale-105 bg-blue-300 border-blue-350 border-opacity-50 rounded-lg shadow-xl p-5 rounded text-xl font-bold" to="/game_board" name="start_game">
                                Start Game
                            </Link>
                        }
                        {this.state.gameDS === 'LLIST-survival' &&
                            <Link className="flex justify-center shadow-xl transition duration-500 ease-in-out bg-blue-500 hover:bg-red-500 transform hover:-translate-y-1 hover:scale-105 bg-blue-300 border-blue-350 border-opacity-50 rounded-lg shadow-xl p-5 rounded text-xl font-bold" to="/llist_gameboard" name="start_game">
                                Start Game
                            </Link>
                        }
                        {this.state.gameDS === 'LLIST-standard' &&
                            <Link className="flex justify-center shadow-xl transition duration-500 ease-in-out bg-blue-500 hover:bg-red-500 transform hover:-translate-y-1 hover:scale-105 bg-blue-300 border-blue-350 border-opacity-50 rounded-lg shadow-xl p-5 rounded text-xl font-bold" to="/llist_gameboard" name="start_game">
                                Start Game
                            </Link>
                        }
                    </li>
                    </ul>

                 <div className="space-y-10"><br></br></div>

        </form>

        </div></span></div>

    );
}
}
export default GameInfo;