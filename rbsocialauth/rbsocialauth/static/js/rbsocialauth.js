(function() {


RBSocialAuth = {};


RBSocialAuth.IdentityItem = RB.Config.ListItem.extend({
    defaults: _.defaults({
        allowedToDisconnect: false,
        disconnectURL: null,
        uid: null,
        provider: null,
        showRemove: true
    }, RB.Config.ListItem.prototype.defaults),

    initialize: function() {
        _.super(this).initialize.call(this);

        this.set({
            text: this.get('uid')
        });
    }
});


RBSocialAuth.IdentityItemView = RB.Config.ListItemView.extend({
    actionHandlers: {
        'delete': '_onRemoveClicked'
    },

    template: _.template([
        '<span class="rbsocialauth-identity-provider"><%- provider %></span>',
        '<span class="rbsocialauth-identity-name"><%- text %></span>'
    ].join('')),

    _onRemoveClicked: function() {
        var $form = $('<form/>')
            .attr({
                action: this.model.get('disconnectURL'),
                method: 'POST'
            })
            .append($('<input/>')
                .attr({
                    type: 'hidden',
                    name: 'csrfmiddlewaretoken',
                    value: this.model.collection.csrfToken
                }))
            .append($('<input/>')
                .attr({
                    type: 'hidden',
                    name: 'next',
                    value: window.location.href
                }))
            .submit();
    }
});

RBSocialAuth.ConnectedIdentitiesView = Backbone.View.extend({
    template: _.template([
        '<% if (identities.length === 0) { %>',
        ' <p>There are no accounts linked.</p>',
        '<% } %>',
        '<div class="rbsocialauth-identities"></div>'
    ].join('')),

    initialize: function(options) {
        this.identities = options.identities;
        this.list = null;
        this.listView = null;
        this.collection = null;

        this.collection = new Backbone.Collection(options.identities, {
            model: RBSocialAuth.IdentityItem,
        });
        this.collection.csrfToken = options.csrf_token;

        this.list = new RB.Config.List({}, {
            collection: this.collection
        });
    },

    render: function() {
        var item,
            itemView;

        this.$el.html(this.template({
            identities: this.identities
        }));

        this.listView = new RB.Config.ListView({
            ItemView: RBSocialAuth.IdentityItemView,
            model: this.list
        });

        this.listView.render();
        this.listView.$el
            .addClass('box-recessed')
            .appendTo(this.$('.rbsocialauth-identities'));

        return this;
    }
});


})();
