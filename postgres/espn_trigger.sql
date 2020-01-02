create or replace function espn() returns trigger as
$func$
begin
 new.espn = new.pts + new.trb + (1.4*new.ast) + new.stl + (1.4*new.blk) - (.7*new.tov) + new.fg + (.5*new.fg) - (.8*(new.fga-new.fg)) + (.25*new.ft) - (.8*(new.fta-new.ft));
 return new;
end;
$func$ language plpgsql;

create trigger espn before insert or update on games 
for each row execute procedure espn();
