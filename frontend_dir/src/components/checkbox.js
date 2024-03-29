import styled from 'styled-components'
import React from "react";
const Checkbox = ({title, ...restProps}) => {
    return (
        <div className='checkbox'>
            <StyledCheckBox {...restProps}/>
            <label className="title-">{title}</label>
        </div>
    )
}
const StyledCheckBox = styled.input`
    box-sizing: border-box;
    height: 34px;
    border: 1px solid #5558FA;
    border-radius: 4px;
    outline: none;
    margin-right: 10px;
`
export default Checkbox
