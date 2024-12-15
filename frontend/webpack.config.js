const path = require('path')
const webpack = require('webpack')
const { VueLoaderPlugin } = require('vue-loader')
const HtmlPlugin = require('html-webpack-plugin')

let config = {
    entry:   [
        './main.js',
        './styles/main.css',
        '../node_modules/bootstrap/dist/css/bootstrap.min.css'
    ],
    output:  {
        filename: 'main.js',
        path:     path.resolve(__dirname, 'dist')
    },
    devServer: {
        port: 8080
    },
    plugins: [
        new webpack.ProvidePlugin({
            Vue: 'vue',
            $: 'jquery',
            Cookies: 'js-cookie'
        }),
        new VueLoaderPlugin(),
        new HtmlPlugin({
            template: './index.html'
        }),
        new webpack.DefinePlugin({
            __VUE_OPTIONS_API__: true,
            __VUE_PROD_DEVTOOLS__: false,
            __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
        }),
    ],
    module:  {
        rules: [
            {
                test: /\.(s*)css$/,
                use:  [
                    'style-loader',
                    'css-loader',
                    'sass-loader'
                ]
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif|ico)$/,
                use:  [
                    {
                        loader:  'file-loader',
                        options: {
                            name: '[name].[ext]',
                            esModule: false
                        }
                    }
                ]
            },
            {
                test:    /\.vue$/,
                exclude: /node_modules/,
                loader:  'vue-loader'
            },
            {
                test: /\.m?js$/,
                enforce: 'pre',
                use: ['source-map-loader']
            }
        ]
    }
};


module.exports = (env, argv) => {
    return config
}
