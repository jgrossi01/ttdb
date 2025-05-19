const customRender = {
    option: function(data, escape) {
        return '<div>' + escape(data.text) + '</div>';
    },
    item: function(data, escape) {
        return '<div>' + escape(data.text) + '</div>';
    },
    option_create: function(data, escape) {
        return '<div class="create">Agregar <strong>' + escape(data.input) + '</strong>&hellip;</div>';
    },
    no_results:function(data,escape){
        return '<div class="no-results text-center">Sin resultados para "'+escape(data.input)+'"</div>';
    },
    not_loading:function(data,escape){
        // no default content
    },
    optgroup: function(data) {
        let optgroup = document.createElement('div');
        optgroup.className = 'optgroup';
        optgroup.appendChild(data.options);
        return optgroup;
    },
    optgroup_header: function(data, escape) {
        return '<div class="optgroup-header">' + escape(data.label) + '</div>';
    },
    loading:function(data,escape){
        return '<div class="spinner"></div>';
    },
    dropdown:function(){
        return '<div></div>';
    }
};