import React, { useState } from 'react'; 
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {Grid, TextField} from '@material-ui/core';
import { render } from '@testing-library/react';
class GameInfo extends React.Component {
    constructor(props) {
        super(props);
        this.customNodeRef = React.createRef();
        //let hyparlink = props.hyparlink || new Hyparlink();
        this.state = {level:null, playerList:null, gameDS:null, game_id:null};
        this.handleInput = this.handleInput.bind(this)
    }   
    handleInput = ({ target }) => {
        this.setState({ [target.name]: target.value });
        console.log(this.state)
    };
   getURLfxn =()=>
    {
        let levelU= this.state.level
        let playerListU = this.state.playerList
        let gameDSU = this.state.gameDS
        
        let start_game_url="/game_board/api/start_game/"+ {levelU}+"/"+{playerListU}+"/"+{gameDSU}
        console.log(start_game_url)
        fetch({start_game_url})
        .then(response => response.json())
        .then(data => this.setState({ game_id: data.total }));
        console.log(this.state.game_id)

        
    }
   
render(){
    this.getURLfxn()
    return(
        <Grid container spacing={1} style={{ marginBottom: '5em' }}>
            <Grid item sm={6} md={6} lg={6}>
                <TextField 
                    required 
                    fullWidth
                    name='level'
                    label='Difficulty Level' 
                    value={this.state.level} 
                    onChange={this.handleInput} 
                    style={{ marginBottom: '1em' }} 
                />
                <TextField 
                    required
                    fullWidth
                    name='playerList' 
                    label='players'
                    value={this.state.playerList} 
                    onChange={this.handleInput} 
                    style={{ marginBottom: '1em' }} 
                />
                <TextField 
                    fullWidth 
                    multiline 
                    name='gameDS' 
                    label='DSgame'
                    value={this.state.gameDS} 
                    onChange={this.handleInput} 
                    style={{ marginBottom: '1em' }} 
                />            
            </Grid>
            

            </Grid>
                
    );
}
}
export default GameInfo;
