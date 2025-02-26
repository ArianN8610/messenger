const {
	BalloonEditor,
	Autoformat,
	AutoLink,
	Autosave,
	BalloonToolbar,
	Bold,
	Emoji,
	Essentials,
	FindAndReplace,
	ImageEditing,
	ImageUtils,
	Italic,
	Link,
	Mention,
	Paragraph,
	RemoveFormat,
	SpecialCharacters,
	SpecialCharactersArrows,
	SpecialCharactersCurrency,
	SpecialCharactersEssentials,
	SpecialCharactersLatin,
	SpecialCharactersMathematical,
	SpecialCharactersText,
	Strikethrough,
	Subscript,
	Superscript,
	TextTransformation,
	Underline
} = window.CKEDITOR;

const editorConfig = {
	toolbar: {
		items: [
			'findAndReplace',
			'|',
			'bold',
			'italic',
			'underline',
			'strikethrough',
			'subscript',
			'superscript',
			'removeFormat',
			'|',
			'emoji',
			'specialCharacters',
			'link'
		],
		shouldNotGroupWhenFull: true
	},
	plugins: [
		Autoformat,
		AutoLink,
		Autosave,
		BalloonToolbar,
		Bold,
		Emoji,
		Essentials,
		FindAndReplace,
		ImageEditing,
		ImageUtils,
		Italic,
		Link,
		Mention,
		Paragraph,
		RemoveFormat,
		SpecialCharacters,
		SpecialCharactersArrows,
		SpecialCharactersCurrency,
		SpecialCharactersEssentials,
		SpecialCharactersLatin,
		SpecialCharactersMathematical,
		SpecialCharactersText,
		Strikethrough,
		Subscript,
		Superscript,
		TextTransformation,
		Underline
	],
	balloonToolbar: ['bold', 'italic', '|', 'link'],
	licenseKey: ckeditor_license_key,
	link: {
		addTargetToExternalLinks: true,
		defaultProtocol: 'https://',
		decorators: {
			toggleDownloadable: {
				mode: 'manual',
				label: 'Downloadable',
				attributes: {
					download: 'file'
				}
			}
		}
	},
	mention: {
		feeds: [
			{
				marker: '@',
				feed: [
					/* See: https://ckeditor.com/docs/ckeditor5/latest/features/mentions.html */
				]
			}
		]
	},
	placeholder: 'Write a message...'
};

let ckeditor_instance;

BalloonEditor.create(document.querySelector('#editor'), editorConfig)
	.then(editor => {
		ckeditor_instance = editor;
	})
	.catch(err => {
		console.error(err);
	});
