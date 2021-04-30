
import React, {Componet} from "react";

class TunnelComponet extends React.Component {
    constructor(props){
        super(props);
        this.tunnelRef = React.createRef();

    }
    render() {
        return (
            <button id='tunnelButton' style={{width:"350px", height:"100px", backgroundColor:"#5f5449", border:"Spx solid #5f5449", marginRight:"200px", borderRadius:"50px"}}>
            </button>
            );
    }

}
export default TunnelComponet;