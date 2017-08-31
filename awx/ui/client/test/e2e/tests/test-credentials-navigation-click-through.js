module.exports = {
    beforeEach: function(client, done) {
        const credentials = client.useCss().page.credentials();
        credentials
            .login()
            .navigate()
            .waitForElementVisible('div.spinny')
            .waitForElementNotVisible('div.spinny', done);
    },
    'activity link is visible and takes user to activity stream': function(client) {
        const credentials = client.page.credentials();
        const activityStream = client.page.activityStream();

        credentials.expect.section('@breadcrumb').visible;
        credentials.section.breadcrumb.expect.element('@activity').visible;
        credentials.section.breadcrumb.click('@activity');

        activityStream
            .waitForElementVisible('div.spinny')
            .waitForElementNotVisible('div.spinny')
            .waitForElementVisible('@title')
            .waitForElementVisible('@category');

        activityStream.expect.element('@title').text.contain('CREDENTIALS');
        activityStream.expect.element('@category').value.contain('credential');

        client.end();
    }
};
