import styled from 'styled-components'
const TextArea = ({children, ...restProps}) => {
    return (
        <div>
            <label className="title-">{children}</label>
            <StyledTextArea {...restProps}/>
        </div>
    )
}
const StyledTextArea = styled.textarea`
    box-sizing: border-box;
    height: 80px;
    width: 100%;
    border: 1px solid #5558FA;
    border-radius: 4px;
    outline: none;
    resize: none;
`
export default TextArea