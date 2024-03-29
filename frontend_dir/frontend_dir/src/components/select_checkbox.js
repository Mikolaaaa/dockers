import React from 'react';
import Multiselect from 'multiselect-react-dropdown';

const MultipleSelect = ({options, handleChange, title, state}) => {
    return (
        <div>
            <label className="title-">{title}</label>
            <Multiselect className='MultiSelect' placeholder='Выберите' hidePlaceholder={true} selectedValues = {state}
                options={options}
                displayValue="cat"
                onSelect={handleChange}
                onRemove={handleChange}
            />
        </div>
    );
};

export default MultipleSelect;
