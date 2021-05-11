import React, {Component} from "react";

class SurfaceTunnelComponet extends React.Component {
    constructor(props){
        super(props);
        this.surfaceTunnelRef = React.createRef();
    }
    render(){
        return(
            <button id='SurfaceTunnelButton' style={{width:"150px", height:"100px", backgroundColor:"#5f5449", border:"Spx solid #5f5449", marginRight:"200px", borderRadius:"10px"}}>
            </button>
        )
    }
}
export default SurfaceTunnelComponet;