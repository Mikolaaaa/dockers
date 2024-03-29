import styled from 'styled-components'
const Input = ({children, ...restProps}) => {
    return (
        <div>
            <label className="title-">{children}</label>
            <StyledInput {...restProps}/>
        </div>
    )
}
const StyledInput = styled.input`
    box-sizing: border-box;
    height: 34px;
    width: 100%;
    border: 1px solid #5558FA;
    border-radius: 4px;
    outline: none;
`
export default Input
