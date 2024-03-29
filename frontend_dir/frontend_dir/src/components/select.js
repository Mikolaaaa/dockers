import styled from 'styled-components'
const Select = ({title, children, ...restProps}) => {
    return (
        <div>
            <label className="title-">{title}</label>
            <StyledSelect {...restProps}>
                {children.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </StyledSelect>
        </div>
    )
}
const StyledSelect = styled.select`
    box-sizing: border-box;
    height: 34px;
    width: 100%;
    border: 1px solid #5558FA;
    border-radius: 4px;
    outline: none;
`
export default Select
