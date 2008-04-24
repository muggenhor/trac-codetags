<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="content" class="codetags">
 <div class="wrapper">
  <h1>Code Tags</h1>
  <table class="matches">
   <tr class="caption">
    <th class="matchname">Filename</th>
    <th class="lineno">Line</th>
    <th class="tag">Tag</th>
    <th class="text">Description</th>
   </tr>
   <?cs each:folder = folders ?>
    <tr class="header">
     <th colspan="4"><a href="<?cs var:folder.href ?>"><?cs var:folder.path ?></a></th>
    </tr>
    <?cs each:match = folder.matches ?>
     <tr class="<?cs var:match.class ?>">
      <td class="matchname"><a href="<?cs var:match.href ?>"><?cs var:match.basename ?></a></td>
      <td class="lineno"><?cs var:match.lineno ?></td>
      <td class="tag"><?cs var:match.tag ?></td>
      <td class="text"><?cs var:match.text ?></td>
     </tr>
    <?cs /each ?>
   <?cs /each ?>
  </table>
 </div>
</div>

<?cs include "footer.cs" ?>
